from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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
    ramp_step = Column(Integer, default=50)
    step_ups = Column(Integer, default=6)
    step_downs = Column(Integer, default=4)


class ReadingProgress(Base):
    __tablename__ = "reading_progresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    chapter_index = Column(Integer, nullable=True)
    word_index = Column(Integer, nullable=True)

    document = relationship("Document", backref="reading_progresses")
