import asyncio
import json
import os
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from litellm import completion
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import database
import models
import schema
from document_reader import DocumentReader

# models.Base.metadata.create_all(bind=database.engine)

MODEL = os.getenv("LLM_MODEL")
MAX_TOKENS = 2048
SYSTEM_PROMPT = "You are an assistant designed to create comprehensive questionnaires to evaluate the knowledge and understanding of students on a specific subject. Your questions should be well-structured, thought-provoking, and tailored to the learning objective. Your goal is to foster critical thinking and deeper understanding."
app = FastAPI()

# Setup static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/documents", response_model=List[schema.Document])
async def list_documents(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Document).offset(skip).limit(limit)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return documents


@app.post("/api/documents", response_model=schema.Document)
async def create_document(
    file: UploadFile, db: AsyncSession = Depends(database.get_db)
):
    filename = file.filename
    with open(f"./files/{filename}", "wb") as f:
        f.write(file.file.read())
    db_document = models.Document(path=filename)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document


@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: int, db: AsyncSession = Depends(database.get_db)
):
    db_document = await db.get(models.Document, document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete the file from disk before removing the database entry
    file_path = f"./files/{db_document.path}"
    if os.path.exists(file_path):
        os.remove(file_path)

    await db.delete(db_document)
    await db.commit()
    return {"message": "Document deleted successfully"}


@app.get("/api/documents/{id}", response_model=schema.DocumentDetail)
async def get_document(id: int, db: AsyncSession = Depends(database.get_db)):
    doc = await db.get(models.Document, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_reader = DocumentReader(doc.path)
    chapters = doc_reader.get_chapter_titles()
    reading_progresses = await db.execute(
        select(models.ReadingProgress).where(models.ReadingProgress.document_id == id)
    )
    chapter_progress = {}
    for rp in reading_progresses.scalars():
        if rp.word_index is None:
            progress = 100
        elif rp.total_words and rp.chapter_id:
            progress = int(rp.word_index * 100 / rp.total_words)
        chapter_progress[rp.chapter_id] = {
            "progress": progress,
            "updated_at": rp.updated_at,
        }
    for ch in chapters:
        if ch["id"] in chapter_progress:
            ch.update(chapter_progress[ch["id"]])
    return {"id": doc.id, "path": doc.path, "chapters": chapters}


@app.get("/api/documents/{document_id}/content")
async def get_content(
    document_id: int,
    words_per_minute: int,
    sprint_minutes: int,
    chapter_id: Optional[int] = None,
    db: AsyncSession = Depends(database.get_db),
):
    doc = await db.get(models.Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_reader = DocumentReader(doc.path)
    if chapter_id:
        content_future = asyncio.create_task(doc_reader.get_chapter_content(chapter_id))
    else:
        content_future = asyncio.create_task(doc_reader.get_content())
    config_query = await db.execute(select(models.ReadingConfig))
    config_query.scalar()
    progress_query = await db.execute(
        select(models.ReadingProgress).where(
            models.ReadingProgress.document_id == document_id,
            models.ReadingProgress.chapter_id == chapter_id,
        )
    )
    reading_progress = progress_query.scalar()
    if reading_progress:
        start_index = reading_progress.word_index
        if start_index is None:
            start_index = 0
    else:
        start_index = 0
    end_index = start_index + (words_per_minute * sprint_minutes)
    content = await content_future
    content = content.replace("\n", " <br> ").split()
    total_words = len(content)
    if end_index >= total_words:
        end_index = None
    else:
        while end_index > start_index and not content[end_index - 1].endswith("."):
            end_index -= 1
    return {
        "content": content[start_index:end_index],
        "start_index": start_index,
        "next_index": end_index,
        "total_words": total_words,
        "title": doc.path,
    }


@app.get("/api/reading_config", response_model=schema.ReadingConfig)
async def get_reading_config(db: AsyncSession = Depends(database.get_db)):
    query = await db.execute(select(models.ReadingConfig))
    reading_config = query.scalar()
    if not reading_config:
        reading_config = models.ReadingConfig()
        db.add(reading_config)
        await db.commit()
        await db.refresh(reading_config)
    return reading_config


@app.put("/api/reading_configs/{config_id}", response_model=schema.ReadingConfig)
async def update_reading_config(
    config_id: int,
    reading_config_update: schema.ReadingConfig,
    db: AsyncSession = Depends(database.get_db),
):
    reading_config = await db.get(models.ReadingConfig, config_id)
    if not reading_config:
        raise HTTPException(
            status_code=404, detail=f"ReadingConfig with id {config_id} not found"
        )
    for key, value in reading_config_update.dict(exclude_unset=True).items():
        setattr(reading_config, key, value)
    await db.commit()
    await db.refresh(reading_config)
    return reading_config


@app.get("/api/reading_progress", response_model=schema.ReadingProgress | None)
async def get_reading_progress(
    document_id: int,
    chapter_id: Optional[int] = None,
    db: AsyncSession = Depends(database.get_db),
):
    query = await db.execute(
        select(models.ReadingProgress).where(
            models.ReadingProgress.document_id == document_id
            and models.ReadingProgress.chapter_id == chapter_id
        )
    )
    reading_progress = query.scalar()
    return reading_progress


@app.put("/api/reading_progress", response_model=schema.ReadingProgress)
async def update_reading_progress(
    reading_progress: schema.ReadingProgress,
    db: AsyncSession = Depends(database.get_db),
):
    query = await db.execute(
        select(models.ReadingProgress).where(
            (models.ReadingProgress.document_id == reading_progress.document_id)
            & (models.ReadingProgress.chapter_id == reading_progress.chapter_id)
        )
    )
    reading_progress_obj = query.scalar()
    if reading_progress_obj:
        for key, value in reading_progress.dict(exclude="id").items():
            setattr(reading_progress_obj, key, value)
    else:
        reading_progress_obj = models.ReadingProgress(
            **reading_progress.dict(exclude="id")
        )
        db.add(reading_progress_obj)
    await db.commit()
    await db.refresh(reading_progress_obj)
    return reading_progress_obj


@app.get("/api/test", response_model=List[schema.Question])
async def get_test(
    document_id: int,
    start_index: int,
    chapter_id: Optional[int] = None,
    end_index: Optional[int] = None,
    db: AsyncSession = Depends(database.get_db),
):
    doc = await db.get(models.Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_reader = DocumentReader(doc.path)
    if chapter_id:
        content = await doc_reader.get_chapter_content(chapter_id)
    else:
        content = await doc_reader.get_content()
    content = content.replace("\n", " <br> ").split()[start_index:end_index]
    content = " ".join(content).replace(" <br> ", "\n")
    prompt = f"""Generate a list of distinct, definitive, and closed-ended questions from the context of the provided text to evaluate comprehension. Each question should have a single correct answer, and the options for each question should be diverse and valid. Present the output in a clear and concise JSON format. Format: `[{{"question": "", "options": ["", "", "", ""], "right_answer": index}}]`. Do not include any additional text or comments in your response apart from the valid json.

    Text:
    {content}"""

    response = completion(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    try:
        questions = json.loads(response.choices[0].message.content)
        valid_questions = [schema.Question(**q) for q in questions]
        return valid_questions
    except json.decoder.JSONDecodeError as e:
        print(response.choices[0].message.content)
        raise e
    except ValidationError as e:
        print(response.choices[0].message.content)
        raise e


@app.post("/api/test_score")
async def evaluate_test(
    test_score: schema.TestScore, db: AsyncSession = Depends(database.get_db)
):
    test_score = models.TestScore(**test_score.dict())
    db.add(test_score)
    await db.commit()
    await db.refresh(test_score)
    return test_score


@app.get("/")
async def home(request: Request):
    return FileResponse("static/index.html")
