"""
Load CSV Data into Database - ETL Testing Script.

This script allows the ETL developer to test loading generated CSV files
into the database. This ensures the ETL process works end-to-end.

Usage:
    python load_data_to_db.py

Prerequisites:
    - CSV files must be generated first (run generate_university_data.py)
    - DATABASE_URL must be set in .env file
    - Database must be running and accessible
"""

import pandas as pd
from loguru import logger
import os
from Database.database import engine, get_db
from Database.models import (
    Student, Location, Instructor, Department, Program, Course,
    TimeSlot, Section, Prerequisites, Takes, Works, HasCourse,
    create_tables
)

# Mapping of CSV table names to SQLAlchemy models
TABLE_MODELS = {
    "student": Student,
    "location": Location,
    "instructor": Instructor,
    "department": Department,
    "program": Program,
    "course": Course,
    "time_slot": TimeSlot,
    "section": Section,
    "prerequisites": Prerequisites,
    "takes": Takes,
    "works": Works,
    "hascourse": HasCourse,
}

# Order matters for foreign key dependencies
LOAD_ORDER = [
    "location",      # No dependencies
    "student",       # No dependencies
    "instructor",    # Depends on location
    "department",    # Depends on location
    "program",       # Depends on department, student
    "course",        # No dependencies
    "time_slot",     # No dependencies
    "section",       # Depends on location, time_slot, course, instructor
    "prerequisites", # Depends on course
    "takes",         # Depends on student, section
    "works",         # Depends on instructor, department
    "hascourse",     # Depends on program, course
]


def load_csv_to_db(csv_path: str, model_class, db_session):
    """
    Load a CSV file into the database using the specified model.
    
    Args:
        csv_path: Path to the CSV file
        model_class: SQLAlchemy model class
        db_session: Database session
    """
    if not os.path.exists(csv_path):
        logger.warning(f"CSV file not found: {csv_path}, skipping...")
        return 0
    
    df = pd.read_csv(csv_path)
    if df.empty:
        logger.warning(f"CSV file is empty: {csv_path}, skipping...")
        return 0
    
    # Convert DataFrame rows to model instances
    records = []
    for _, row in df.iterrows():
        # Convert row to dictionary, handling NaN values
        record_dict = row.to_dict()
        # Remove NaN values (convert to None for nullable fields)
        record_dict = {k: (None if pd.isna(v) else v) for k, v in record_dict.items()}
        
        try:
            record = model_class(**record_dict)
            records.append(record)
        except Exception as e:
            logger.error(f"Error creating {model_class.__name__} from row: {record_dict}")
            logger.error(f"Error: {e}")
            raise
    
    # Bulk insert
    try:
        db_session.bulk_save_objects(records)
        db_session.commit()
        logger.info(f"Loaded {len(records)} records from {csv_path} into {model_class.__tablename__}")
        return len(records)
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error loading {csv_path} into database: {e}")
        raise


def main():
    """Main function to load all CSV files into the database."""
    logger.info("Starting CSV to database load process...")
    
    # Create tables if they don't exist
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created/verified.")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        data_dir = "data"
        total_records = 0
        
        # Load tables in dependency order
        for table_name in LOAD_ORDER:
            csv_path = os.path.join(data_dir, f"{table_name}.csv")
            model_class = TABLE_MODELS[table_name]
            
            logger.info(f"Loading {table_name}...")
            count = load_csv_to_db(csv_path, model_class, db)
            total_records += count
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SUCCESS: Loaded {total_records} total records into database")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

