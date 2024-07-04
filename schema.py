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
