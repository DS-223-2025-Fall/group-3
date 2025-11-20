"""
Database Configuration for Notebook
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


# Load environment variables from .env file
# Try multiple locations for .env file (in case running locally)
load_dotenv("/notebook/.env")
load_dotenv("/notebook/../.env")  # Parent directory
load_dotenv()  # Current directory

# Get the database URL from environment variables
# Docker-compose will pass this as an environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# SessionLocal for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """
    Function to get a database session.
    Returns a database session (caller should close it).
    """
    return SessionLocal()
