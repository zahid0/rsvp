from typing import List

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import database
import models
import schema

# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/content")
async def content():
    with open("files/data.txt", "r") as file:
        content = file.read().replace("\n", " <br> ")
    return {"content": content.split()}


@app.get("/api/documents", response_model=List[schema.Document])
async def read_documents(
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
