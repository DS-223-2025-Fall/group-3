"""
Database Configuration for Notebook
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import time


# Load environment variables from .env file
# Try multiple locations: Docker mount, parent directory, current directory
load_dotenv("/notebook/.env")     # Docker mount location
load_dotenv("../.env")            # Parent directory (for local dev)
load_dotenv()                     # Current directory

# Get the database URL from environment variables
# Docker-compose will pass this as an environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using them
    pool_recycle=3600,       # Recycle connections after 1 hour
    pool_size=10,            # Connection pool size
    max_overflow=20,         # Max overflow connections
    echo=False               # Set to True for SQL query logging
)

# Base class for declarative models (must be defined before importing models)
Base = declarative_base()

# SessionLocal for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def reflect_referenced_tables():
    """
    Reflect tables that are referenced by foreign keys but not defined as models.
    This ensures SQLAlchemy can validate foreign key relationships.
    Should be called after importing models.
    """
    # Tables that are referenced by foreign keys but not defined in notebook models
    tables_to_reflect = ['time_slots', 'students', 'courses', 'sections']
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Only reflect tables that exist and aren't already in metadata
        for table_name in tables_to_reflect:
            if table_name in existing_tables and table_name not in Base.metadata.tables:
                Base.metadata.reflect(bind=engine, only=[table_name])
    except Exception as e:
        # If reflection fails, continue anyway
        pass


def get_db_session():
    """
    Function to get a database session.
    Returns a database session (caller should close it).
    
    DEPRECATED: Use get_db() generator pattern instead for automatic cleanup.
    
    Example:
        db = get_db_session()
        try:
            # Use db session
            students = db.query(Student).all()
        finally:
            db.close()
    """
    return SessionLocal()


def get_db():
    """
    Description:
        Get a database session for dependency injection. Yields a database session and ensures it's closed after use.
        This is the recommended pattern for session management.
    
    Input:
        None
    
    Output:
        Generator[Session]: Database session generator that yields a session
    
    Example:
        for db in get_db():
            students = db.query(Student).all()
            break  # Generator will close session automatically
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection(max_retries=5, retry_delay=2):
    """
    Check if database connection is available.
    Retries connection with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
    
    Returns:
        True if connection successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"⚠ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"✗ Database connection failed after {max_retries} attempts: {e}")
                return False
    return False


def verify_tables_exist(table_names=None):
    """
    Verify that required database tables exist.
    
    Args:
        table_names: List of table names to check. If None, checks common tables.
    
    Returns:
        Dictionary with table existence status
    """
    if table_names is None:
        table_names = [
            'students', 'courses', 'sections', 'takes', 
            'prerequisites', 'programs', 'hascourse', 'time_slots'
        ]
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        result = {}
        for table in table_names:
            exists = table in existing_tables
            result[table] = exists
            if exists:
                # Get row count
                with engine.connect() as conn:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    result[f"{table}_count"] = count
        
        return result
    except SQLAlchemyError as e:
        print(f"Error checking tables: {e}")
        return {table: False for table in table_names}
