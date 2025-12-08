"""
Database configuration for the ETL process.
"""

import os
from typing import Generator

import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from dotenv import load_dotenv

# Load environment variables from .env file
# Try multiple locations: Docker mount, parent directory, current directory
load_dotenv("/etl/.env")     # Docker mount location
load_dotenv("../.env")       # Parent directory (for local dev)
load_dotenv()                # Current directory

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Define it in your .env file or export it in the environment."
    )

engine = sql.create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using them
    pool_recycle=3600,       # Recycle connections after 1 hour
    pool_size=10,            # Connection pool size
    max_overflow=20          # Max overflow connections
)
Base = declarative.declarative_base()
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[orm.Session, None, None]:
    """
    Description:
        Provides a database session for performing ORM operations and closes it when done.
    
    Input:
        None
    
    Output:
        Generator that yields a `sqlalchemy.orm.Session` instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
