"""
Database Initialization Module
Checks if database is empty and initializes it by running ETL if needed.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from sqlalchemy import inspect
from Database.database import engine, get_db
from Database.models import StudentDB, CourseDB, ProgramDB, SectionDB, Base


def is_database_initialized():
    """
    Check if database is fully initialized by checking multiple key tables.
    Returns True if database has data, False if empty.
    """
    try:
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("No tables found - database is empty")
            return False
        
        # Check if key tables have data
        db = next(get_db())
        try:
            checks = {
                'students': db.query(StudentDB).count(),
                'courses': db.query(CourseDB).count(),
                'programs': db.query(ProgramDB).count(),
                'sections': db.query(SectionDB).count(),
            }
            
            # Database is initialized if ALL key tables have data
            is_initialized = all(count > 0 for count in checks.values())
            
            if is_initialized:
                logger.info(f"Database already initialized: {checks}")
                return True
            else:
                logger.info(f"Database appears incomplete: {checks}")
                return False
        finally:
            db.close()
    except Exception as e:
        # If we can't check (e.g., tables don't exist), assume empty
        logger.warning(f"Could not check database status: {e}. Assuming empty.")
        return False


def initialize_database():
    """
    Initialize the database by running the ETL process.
    This should only be called if the database is empty.
    """
    try:
        # Find the ETL directory (mounted at /etl)
        etl_dir = Path("/etl")
        
        if not etl_dir.exists():
            logger.error("ETL directory not found at /etl. Cannot initialize database.")
            return False
        
        # Add ETL directory to Python path
        sys.path.insert(0, str(etl_dir))
        sys.path.insert(0, str(etl_dir / "Database"))
        
        logger.info("Running ETL process to initialize database...")
        
        # Import and run ETL functions directly
        try:
            # Step 1: Generate data
            logger.info("Step 1: Generating university data...")
            from generate_university_data import main as generate_main
            generate_main()
            
            # Step 2: Load data
            logger.info("Step 2: Loading data into database...")
            from load_data_to_db import main as load_main
            load_main()
            
            logger.info("Database initialization completed successfully!")
            return True
            
        except ImportError as e:
            logger.error(f"Could not import ETL modules: {e}")
            logger.error("Make sure ETL directory is mounted and dependencies are installed.")
            return False
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def ensure_database_initialized():
    """
    Main function to ensure database is initialized.
    Checks if database is empty and runs ETL if needed.
    """
    logger.info("Checking if database needs initialization...")
    
    # First, ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False
    
    # Check if database is initialized
    if is_database_initialized():
        logger.info("Database is already initialized. Skipping ETL.")
        return True
    
    # Database is empty, run initialization
    logger.info("Database is empty. Running initialization...")
    return initialize_database()

