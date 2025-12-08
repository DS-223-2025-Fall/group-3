"""
Database configuration module for SQLAlchemy connection setup.
Provides database engine, base class, and session management for the application.

This module handles database connection initialization and provides a dependency
injection function for FastAPI endpoints to access database sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


# Load environment variables from .env file
# Try multiple locations: Docker mount, parent directory, current directory
load_dotenv("/api/.env")     # Docker mount location
load_dotenv("../.env")       # Parent directory (for local dev)
load_dotenv()                # Current directory

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using them
    pool_recycle=3600,       # Recycle connections after 1 hour
    pool_size=10,            # Connection pool size
    max_overflow=20          # Max overflow connections
)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Description:
    Get a database session for dependency injection. Yields a database session and ensures it's closed after use.
    
    Input:
        None
    
    Output:
        Generator[Session]: Database session generator that yields a session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()