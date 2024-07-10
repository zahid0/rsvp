from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel


class Document(BaseModel):
    id: int
    path: str

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    file: UploadFile


class Chapter(BaseModel):
    id: int
    title: str


class ReadingConfig(BaseModel):
    id: int
    words_per_minute: int
    number_of_words: int
    font_size: int
    sprint_minutes: int
    ramp_step: int
    step_ups: int
    step_downs: int


class ReadingProgress(BaseModel):
    id: Optional[int] = None
    document_id: int
    chapter_id: Optional[int] = None
    word_index: Optional[int] = None


class TestScore(BaseModel):
    words_per_minute: int
    score: int
