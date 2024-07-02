from pydantic import BaseModel


class Entry(BaseModel):
    id: int
    path: str

    class Config:
        orm_mode = True


class EntryCreate(BaseModel):
    path: str
