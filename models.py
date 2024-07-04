from sqlalchemy import Column, Integer, String

from database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path = Column(String, index=True, unique=True)


class ReadingConfig(Base):
    __tablename__ = "reading_configs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    words_per_minute = Column(Integer, default=300)
    number_of_words = Column(Integer, default=5)
    font_size = Column(Integer, default=64)
    sprint_minutes = Column(Integer, default=5)
