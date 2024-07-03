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
    content = doc_reader.get_chapter_content(chapter_id).replace("\n", " <br> ")
    return {"content": content.split()}


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
