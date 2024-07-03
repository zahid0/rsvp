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
