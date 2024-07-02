from sqlalchemy import Column, Integer, String

from database import Base


class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path = Column(String, index=True, unique=True)
