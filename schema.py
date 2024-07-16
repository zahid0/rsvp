from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel, ValidationError, validator


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


class DocumentDetail(BaseModel):
    id: int
    path: str
    chapters: List[Chapter]


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


class Question(BaseModel):
    question: str
    options: List[str]
    right_answer: int

    @validator("right_answer")
    def right_answer_validator(cls, value, values):
        if "options" not in values:
            raise ValidationError("'options' key is not present in the JSON object.")
        if value < 0 or value >= len(values["options"]):
            raise ValueError("right_answer index is out of range for options")
        return value


class TestScore(BaseModel):
    words_per_minute: int
    score: int
