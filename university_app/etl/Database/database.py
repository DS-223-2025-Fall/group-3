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
# Try multiple locations: parent directory (for local dev) and current directory
load_dotenv("../.env")  # Parent directory (university_app/.env)
load_dotenv(".env")     # Current directory (for Docker if mounted)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Define it in your .env file or export it in the environment."
    )

engine = sql.create_engine(DATABASE_URL)
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
