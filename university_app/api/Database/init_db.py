"""
Database initialization module for the API service.
Checks if database is empty and initializes it by running ETL process if needed.
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
    Check if database is fully initialized by checking multiple key tables for data.
    
    Input:
        None
    
    Return:
        bool: True if database has data, False if empty.
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
    Initialize the database by running the ETL process. Always runs ETL to ensure database has fresh data.
    
    Input:
        None
    
    Return:
        bool: True if initialization successful, False otherwise.
    """
    try:
        # Find the ETL directory (mounted at /etl)
        etl_dir = Path("/etl")
        
        if not etl_dir.exists():
            logger.error("ETL directory not found at /etl. Cannot initialize database.")
            return False
        
        # Add ETL directory to Python path (must be before any imports)
        etl_path = str(etl_dir)
        etl_db_path = str(etl_dir / "Database")
        
        # Remove if already in path to avoid duplicates
        if etl_path in sys.path:
            sys.path.remove(etl_path)
        if etl_db_path in sys.path:
            sys.path.remove(etl_db_path)
            
        # Insert at the beginning so they're checked first
        sys.path.insert(0, etl_db_path)  # Database directory first (for imports)
        sys.path.insert(0, etl_path)      # ETL root second
        
        logger.info("Running ETL process to initialize database...")
        
        # Run ETL process using subprocess to avoid import path issues
        try:
            import subprocess
            
            # Step 1: Generate data
            logger.info("Step 1: Generating university data...")
            result1 = subprocess.run(
                ["python", "generate_university_data.py"],
                cwd=etl_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result1.returncode != 0:
                logger.error(f"Data generation failed: {result1.stderr}")
                return False
            logger.info("Data generation completed successfully")
            
            # Step 2: Load data
            logger.info("Step 2: Loading data into database...")
            result2 = subprocess.run(
                ["python", "load_data_to_db.py"],
                cwd=etl_path,
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "PYTHONPATH": f"{etl_path}:{etl_path}/Database"}
            )
            if result2.returncode != 0:
                logger.error(f"❌ Data loading failed with return code {result2.returncode}")
                logger.error(f"STDERR:\n{result2.stderr}")
                logger.error(f"STDOUT:\n{result2.stdout}")
                # Also check for specific table loading issues
                if "section_name" in result2.stderr or "section_name" in result2.stdout:
                    logger.error("⚠️  section_name table loading issue detected!")
                if "users" in result2.stderr or "users" in result2.stdout:
                    logger.error("⚠️  users table loading issue detected!")
                return False
            logger.info("Data loading completed successfully")
            
            # Verify critical tables were loaded
            logger.info("Verifying critical tables were loaded...")
            db = next(get_db())
            try:
                from Database.models import UserDB, SectionNameDB
                user_count = db.query(UserDB).count()
                section_name_count = db.query(SectionNameDB).count()
                logger.info(f"Verification: users={user_count}, section_name={section_name_count}")
                if user_count == 0:
                    logger.warning("⚠️  WARNING: users table is empty after loading!")
                if section_name_count == 0:
                    logger.warning("⚠️  WARNING: section_name table is empty after loading!")
            except Exception as e:
                logger.warning(f"Could not verify table counts: {e}")
            finally:
                db.close()
            
            logger.info("Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            logger.error(f"ETL path: {etl_path}")
            logger.error("Make sure ETL directory is mounted and dependencies are installed.")
            return False
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def ensure_database_initialized():
    """
    Main function to ensure database is initialized. Always runs ETL to ensure database has data (will handle existing data gracefully).
    
    Input:
        None
    
    Return:
        bool: True if initialization successful, False otherwise.
    """
    logger.info("Ensuring database is initialized...")
    
    # Drop the old 'user' table if it exists (PostgreSQL reserved word issue)
    # We now use 'users' table name instead
    try:
        from sqlalchemy import text, inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'user' in tables:
            logger.warning("Found old 'user' table (reserved word). Migrating to 'users'...")
            with engine.connect() as connection:
                # Check if data exists in old table
                result = connection.execute(text("SELECT COUNT(*) FROM \"user\""))
                count = result.fetchone()[0]
                if count > 0:
                    logger.info(f"Found {count} records in old 'user' table")
                    # Copy data to new table if users doesn't exist or is empty
                    users_count = connection.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0] if 'users' in tables else 0
                    if users_count == 0:
                        logger.info("Copying data from 'user' to 'users'...")
                        connection.execute(text("INSERT INTO users SELECT * FROM \"user\""))
                        connection.commit()
                # Drop the old table
                connection.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE"))
                connection.commit()
            logger.info("Migrated from 'user' to 'users' table successfully.")
    except Exception as e:
        logger.warning(f"Could not migrate 'user' table: {e}. Continuing...")
    
    # First, ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False
    
    # Always run ETL - it will handle existing data gracefully
    logger.info("Running ETL to initialize/refresh database...")
    if initialize_database():
        logger.info("Database initialization completed successfully via ETL.")
        return True
    else:
        logger.error("ETL initialization failed. Database may be incomplete.")
        logger.warning("To manually initialize database, run: docker compose run --rm etl bash run_etl.sh")
        return False

