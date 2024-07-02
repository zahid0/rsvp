from typing import List

from fastapi import Depends, FastAPI
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
def home():
    return FileResponse("templates/index.html")


@app.get("/content")
def content():
    with open("files/data.txt", "r") as file:
        content = file.read().replace("\n", " <br> ")
    return {"content": content.split()}


@app.get("/entries/", response_model=List[schema.Entry])
async def read_entries(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Entry).offset(skip).limit(limit)
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return entries


@app.post("/entries/", response_model=schema.Entry)
async def create_entry(
    entry: schema.EntryCreate, db: AsyncSession = Depends(database.get_db)
):
    db_entry = models.Entry(path=entry.path)
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry
