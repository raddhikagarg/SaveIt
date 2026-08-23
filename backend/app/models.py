from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saveit.db")
# Falls back to a local SQLite file if no DATABASE_URL is set yet —
# this means you can run everything right now without setting up Postgres at all.
# Swap in your real Postgres URL in .env once it's ready; no code changes needed.

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TrackerEntry(Base):
    __tablename__ = "tracker_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    category = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    eligibility = Column(Text, nullable=True)
    stipend = Column(String, nullable=True)
    source_link = Column(String, nullable=True)
    source_type = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    deadline_source = Column(String, nullable=True)   # "reel" | "linked_page" | "web_search"
    user_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResourceEntry(Base):
    __tablename__ = "resource_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    items = Column(Text, nullable=False)   # stored as JSON string, parsed back into a list on read
    source_link = Column(String, nullable=True)
    source_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency used in routers to get a database session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables. Call this once on startup."""
    Base.metadata.create_all(bind=engine)
