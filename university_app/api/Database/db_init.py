"""
Database initialization and health check utilities.
Provides functions for database connection health checks, schema initialization, and optional database seeding.
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from Database.database import engine, Base, SessionLocal
# Import models as they're added to the project
# from Database.models import StudentDB, CourseDB, etc.
from loguru import logger
import sys


def check_db_connection() -> bool:
    """
    Check if the database connection is healthy and accessible.
    
    Input:
        None
    
    Return:
        bool: True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection check: SUCCESS")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection check: FAILED - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Database connection check: UNEXPECTED ERROR - {str(e)}")
        return False


def init_database() -> bool:
    """
    Initialize the database by creating all tables. Safe to run multiple times (won't recreate existing tables).
    
    Input:
        None
    
    Return:
        bool: True if initialization successful, False otherwise.
    """
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialization: SUCCESS - All tables created")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database initialization: FAILED - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Database initialization: UNEXPECTED ERROR - {str(e)}")
        return False


def drop_all_tables() -> bool:
    """
    Drop all database tables. USE WITH CAUTION! This will delete all data in the database.
    
    Input:
        None
    
    Return:
        bool: True if successful, False otherwise.
    
    Warning:
        This will permanently delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped!")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        return False


def reset_database() -> bool:
    """
    Reset the database by dropping all tables and recreating them. USE WITH CAUTION - This will delete all data!
    
    Input:
        None
    
    Return:
        bool: True if successful, False otherwise.
    """
    logger.warning("Resetting database - all data will be lost!")
    if drop_all_tables() and init_database():
        logger.info("Database reset: SUCCESS")
        return True
    else:
        logger.error("Database reset: FAILED")
        return False


def get_database_info() -> dict:
    """
    Get information about the database connection and schema including database name and table list.
    
    Input:
        None
    
    Return:
        dict: Dictionary with database information including database_name, tables, table_count, and connection_status.
    """
    try:
        with engine.connect() as connection:
            # Get database name
            db_name_result = connection.execute(text("SELECT current_database()"))
            db_name = db_name_result.fetchone()[0]
            
            # Get list of tables
            tables_result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in tables_result.fetchall()]
            
            return {
                "database_name": db_name,
                "tables": tables,
                "table_count": len(tables),
                "connection_status": "connected"
            }
    except SQLAlchemyError as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {
            "database_name": "unknown",
            "tables": [],
            "table_count": 0,
            "connection_status": "error",
            "error": str(e)
        }


def seed_database(sample_data: bool = False) -> bool:
    """
    Seed the database with initial or sample data. This is a placeholder function that can be implemented based on specific needs.
    
    Input:
        sample_data (bool): If True, add sample data for testing, default False.
    
    Return:
        bool: True if seeding successful, False otherwise.
    """
    try:
        db = SessionLocal()
        
        if sample_data:
            # Example: Add sample data
            # Uncomment and import models as needed:
            # from Database.models import StudentDB
            # sample_student = StudentDB(
            #     student_name="Sample Student",
            #     credit=0
            # )
            # db.add(sample_student)
            # db.commit()
            logger.info("Sample data seeding - implement based on your models")
        
        db.close()
        logger.info("Database seeding: SUCCESS")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database seeding: FAILED - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Database seeding: UNEXPECTED ERROR - {str(e)}")
        return False


if __name__ == "__main__":
    """
    Run database initialization from command line.
    
    Usage:
        python -m Database.db_init
    """
    logger.info("Starting database initialization...")
    
    # Check connection
    if not check_db_connection():
        logger.error("Cannot connect to database. Exiting.")
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        logger.error("Database initialization failed. Exiting.")
        sys.exit(1)
    
    # Get database info
    info = get_database_info()
    logger.info(f"Database: {info['database_name']}")
    logger.info(f"Tables: {info['table_count']}")
    logger.info("Database initialization complete!")

