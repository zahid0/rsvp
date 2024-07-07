from typing import Optional

from pydantic import BaseModel


class Document(BaseModel):
    id: int
    path: str

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    path: str


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
    chapter_index: Optional[int] = None
    word_index: int | None
