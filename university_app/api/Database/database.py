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
load_dotenv(".env")

# Get the database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Base class for declarative models
Base = declarative_base()

# SessionLocal for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get a database session for dependency injection. Yields a database session and ensures it's closed after use.
    
    Input:
        None
    
    Return:
        Generator[Session]: Database session generator that yields a session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()