import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async sessionmaker
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
# Function to get async session
async def get_db():
    async with SessionLocal() as session:
        yield session
