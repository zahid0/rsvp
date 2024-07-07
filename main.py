from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import database
import models
import schema
from document_reader import DocumentReader

# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
    document: schema.DocumentCreate, db: AsyncSession = Depends(database.get_db)
):
    db_document = models.Document(path=document.path)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document


@app.get("/api/documents/{id}", response_model=schema.Document)
async def get_document(id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.get(models.Document, id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@app.get("/api/documents/{id}/chapters", response_model=List[schema.Chapter])
async def get_document_chapters(id: int, db: AsyncSession = Depends(database.get_db)):
    doc = await db.get(models.Document, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_reader = DocumentReader(doc.path)
    return doc_reader.get_chapters()


@app.get("/api/documents/{document_id}/chapters/{chapter_id}")
async def get_chapter_content(
    document_id: int, chapter_id: int, db: AsyncSession = Depends(database.get_db)
):
    doc = await db.get(models.Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_reader = DocumentReader(doc.path)
    content = doc_reader.get_chapter_content(chapter_id).replace("\n", " <br> ").split()
    config_query = await db.execute(select(models.ReadingConfig))
    reading_config = config_query.scalar()
    progress_query = await db.execute(
        select(models.ReadingProgress).where(
            models.ReadingProgress.document_id == document_id
            and model.ReadingProgress.chapter_index == chapter_index
        )
    )
    reading_progress = progress_query.scalar()
    if reading_progress:
        start_index = reading_progress.word_index
        if start_index is None:
            start_index = 0
    else:
        start_index = 0
    if reading_config:
        end_index = start_index + (
            reading_config.words_per_minute * reading_config.sprint_minutes
        )
        if end_index >= len(content):
            end_index = None
        else:
            while end_index > start_index and not content[end_index - 1].endswith("."):
                end_index -= 1
    else:
        end_index = None
    return {
        "content": content[start_index:end_index],
        "start_index": start_index,
        "next_index": end_index,
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
    chapter_index: int | None = None,
    db: AsyncSession = Depends(database.get_db),
):
    query = await db.execute(
        select(models.ReadingProgress).where(
            models.ReadingProgress.document_id == document_id
            and model.ReadingProgress.chapter_index == chapter_index
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
            models.ReadingProgress.document_id == reading_progress.document_id
            and model.ReadingProgress.chapter_index == reading_progress.chapter_index
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


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/documents/{id}")
async def home(id: int, request: Request):
    return templates.TemplateResponse(
        "document.html", {"document_id": id, "request": request}
    )


@app.get("/documents/{document_id}/chapters/{chapter_id}")
async def home(document_id: int, chapter_id: int, request: Request):
    return templates.TemplateResponse(
        "chapter.html",
        {"document_id": document_id, "chapter_id": chapter_id, "request": request},
    )
