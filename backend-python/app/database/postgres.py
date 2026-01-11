"""
PostgreSQL Database Connection

MVP: Simple PostgreSQL connection for concept storage.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp")

# Create engine
engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG", "False").lower() == "true")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_connection():
    """Check database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
