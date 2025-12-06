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
from sqlalchemy import text
from Database.database import engine, get_db
from Database.models import (
    User, Student, Location, Instructor, Department, Program, Course,
    TimeSlot, Section, SectionName, Prerequisites, Takes, Works, HasCourse,
    Cluster, CourseCluster, Preferred,
    create_tables
)

# Mapping of CSV table names to SQLAlchemy models
TABLE_MODELS = {
    "users": User,
    "student": Student,
    "location": Location,
    "instructor": Instructor,
    "department": Department,
    "program": Program,
    "course": Course,
    "time_slot": TimeSlot,
    "section": Section,
    "section_name": SectionName,
    "prerequisites": Prerequisites,
    "takes": Takes,
    "works": Works,
    "hascourse": HasCourse,
    "cluster": Cluster,
    "course_cluster": CourseCluster,
    "preferred": Preferred,
}

# Order matters for foreign key dependencies
LOAD_ORDER = [
    "location",       # No dependencies
    "student",        # No dependencies
    "users",          # Depends on student
    "instructor",     # Depends on location
    "department",     # Depends on location
    "program",        # Depends on department
    "course",         # No dependencies
    "time_slot",      # No dependencies
    "section",        # Depends on location, time_slot, course, instructor
    "section_name",   # Depends on section
    "prerequisites",  # Depends on course
    "takes",          # Depends on student, section
    "works",          # Depends on instructor, department
    "hascourse",      # Depends on program, course
    "cluster",        # No dependencies
    "course_cluster", # Depends on course, cluster
    "preferred",      # Depends on student, course
]


def load_csv_to_db(csv_path: str, model_class, db_session):
    """
    Description: Load a single CSV file into the corresponding database table using the given model.
    inputs: csv_path (str), model_class (SQLAlchemy model), db_session (SQLAlchemy Session).
    return: Number of records inserted into the table (int).
    """
    if not os.path.exists(csv_path):
        error_msg = f"CSV file not found: {csv_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    df = pd.read_csv(csv_path)
    if df.empty:
        error_msg = f"CSV file is empty: {csv_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Column name mapping: CSV file name -> CSV column -> Model field
    csv_filename = os.path.basename(csv_path).replace(".csv", "")

    column_mapping = {
        "student": {"id": "student_id", "name": "student_name"},
        # Note: program CSV already has dept_name, matching the model field
        # No mapping needed for program table
        # Note: users CSV uses student_id directly (matches model)
        # Note: section_name CSV uses section_name and section_id directly (matches model)
    }

    mapping = column_mapping.get(csv_filename, {})

    # Rename columns if mapping exists
    if mapping:
        df = df.rename(columns=mapping)

    # Special handling for programs - deduplicate by prog_name (primary key)
    if csv_filename == "program":
        df = df.drop_duplicates(subset=["prog_name"], keep="first")
        logger.info(f"Deduplicated programs: {len(df)} unique programs")

    # Special handling for hascourse - deduplicate by (prog_name, courseid) composite key
    if csv_filename == "hascourse":
        original_count = len(df)
        df = df.drop_duplicates(subset=["prog_name", "courseid"], keep="first")
        if len(df) < original_count:
            logger.info(
                f"Deduplicated hascourse: {len(df)} unique records "
                f"(removed {original_count - len(df)} duplicates)"
            )

    # Special handling for section_name - deduplicate by (section_name, section_id) composite key
    if csv_filename == "section_name":
        original_count = len(df)
        df = df.drop_duplicates(subset=["section_name", "section_id"], keep="first")
        if len(df) < original_count:
            logger.info(
                f"Deduplicated section_name: {len(df)} unique records "
                f"(removed {original_count - len(df)} duplicates)"
            )

    # Convert DataFrame rows to model instances
    records = []
    for _, row in df.iterrows():
        record_dict = row.to_dict()
        record_dict = {k: (None if pd.isna(v) else v) for k, v in record_dict.items()}

        try:
            record = model_class(**record_dict)
            records.append(record)
        except Exception as e:
            logger.error(f"Error creating {model_class.__name__} from row: {record_dict}")
            logger.error(f"Error: {e}")
            raise

    # Insert records (using add_all instead of bulk_save_objects to properly handle
    # foreign keys and composite primary keys)
    # For tables with composite primary keys or foreign keys, we need to flush explicitly
    try:
        if len(records) == 0:
            logger.warning(f"No records to insert for {model_class.__tablename__}")
            return 0
        
        # Add records to session
        db_session.add_all(records)
        
        # Flush to send INSERT statements to database (important for foreign key validation)
        # This will raise an error if there are foreign key constraint violations
        db_session.flush()
        
        # Commit the transaction
        db_session.commit()
        
        # Verify the records were actually inserted
        inserted_count = db_session.query(model_class).count()
        logger.info(
            f"Loaded {len(records)} records from {csv_path} into {model_class.__tablename__} "
            f"(verified: {inserted_count} total records in table)"
        )
        return len(records)
    except Exception as e:
        db_session.rollback()
        error_msg = str(e).lower()
        if "duplicate key" in error_msg or "unique constraint" in error_msg:
            logger.error(
                f"Duplicate records detected in {model_class.__tablename__}. "
                f"This may indicate a partial load or data issue. Error: {e}"
            )
            # Don't silently fail - raise the error so we know what went wrong
            raise
        if "foreign key" in error_msg or "violates foreign key constraint" in error_msg:
            logger.error(
                f"Foreign key constraint violation in {model_class.__tablename__}. "
                f"This may indicate missing parent records. Error: {e}"
            )
            if records:
                sample = records[0]
                logger.error(f"Sample record that failed: {sample.__dict__ if hasattr(sample, '__dict__') else 'N/A'}")
            raise
        logger.error(f"Error loading {csv_path} into database: {e}")
        logger.error(f"Model: {model_class.__name__}, Table: {model_class.__tablename__}")
        logger.error(f"Number of records attempted: {len(records)}")
        if records:
            logger.error(f"First record sample: {records[0].__dict__ if hasattr(records[0], '__dict__') else 'N/A'}")
        raise


def main():
    """
    Description: Create tables if needed and load all CSVs into the database in dependency order.
    Clears existing data first to avoid duplicates, then loads fresh data.
    inputs: None; uses global LOAD_ORDER and TABLE_MODELS.
    return: None.
    """
    logger.info("Starting CSV to database load process...")

    # Create tables if they don't exist
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created/verified.")

    # Get database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        # First, clear tables that might have foreign keys to ETL tables (notebook-generated tables)
        # These need to be cleared first to avoid foreign key constraint violations
        logger.info("Clearing notebook-generated tables that reference ETL tables...")
        try:
            # Clear recommendation_results if it exists (created by notebook, references sections)
            db.execute(text("DELETE FROM recommendation_results"))
            logger.info("Cleared recommendation_results table")
        except Exception as e:
            logger.debug(f"Could not clear recommendation_results (may not exist): {e}")
        
        try:
            # Clear ab_test_assignments if it exists
            db.execute(text("DELETE FROM ab_test_assignments"))
            logger.info("Cleared ab_test_assignments table")
        except Exception as e:
            logger.debug(f"Could not clear ab_test_assignments (may not exist): {e}")
        
        try:
            # Clear ui_element_clicks if it exists
            db.execute(text("DELETE FROM ui_element_clicks"))
            logger.info("Cleared ui_element_clicks table")
        except Exception as e:
            logger.debug(f"Could not clear ui_element_clicks (may not exist): {e}")
        
        db.commit()
        
        # Now clear all ETL tables in reverse dependency order to avoid foreign key constraints
        logger.info("Clearing existing data from ETL tables (in reverse dependency order)...")
        for table_name in reversed(LOAD_ORDER):
            model_class = TABLE_MODELS[table_name]
            existing_count = db.query(model_class).count()
            if existing_count > 0:
                logger.info(f"Clearing {existing_count} records from {table_name}...")
                db.query(model_class).delete()
        
        db.commit()
        logger.info("All existing data cleared. Loading fresh data...")

        # Now load tables in dependency order
        data_dir = "data"
        total_records = 0

        for table_name in LOAD_ORDER:
            csv_path = os.path.join(data_dir, f"{table_name}.csv")
            model_class = TABLE_MODELS[table_name]

            logger.info(f"{'=' * 60}")
            logger.info(f"Loading {table_name} (table: {model_class.__tablename__})...")
            logger.info(f"CSV path: {csv_path}")
            
            try:
                # Verify CSV file exists before attempting to load
                if not os.path.exists(csv_path):
                    error_msg = f"CSV file not found: {csv_path}"
                    logger.error(f"❌ {error_msg}")
                    logger.error(f"   Current working directory: {os.getcwd()}")
                    logger.error(f"   Data directory: {os.path.abspath(data_dir)}")
                    logger.error(f"   Files in data directory: {os.listdir(data_dir) if os.path.exists(data_dir) else 'Directory does not exist'}")
                    raise FileNotFoundError(error_msg)
                
                # Check if CSV file is empty
                file_size = os.path.getsize(csv_path)
                if file_size == 0:
                    error_msg = f"CSV file is empty: {csv_path}"
                    logger.error(f"❌ {error_msg}")
                    raise ValueError(error_msg)
                
                logger.info(f"   CSV file found ({file_size} bytes)")
                
                # Verify parent tables exist for foreign key dependencies
                if table_name == "users":
                    student_count = db.query(TABLE_MODELS["student"]).count()
                    logger.info(f"   Parent table 'student' has {student_count} records")
                    if student_count == 0:
                        logger.warning(f"   ⚠️  WARNING: 'student' table is empty! 'users' table requires student records.")
                elif table_name == "section_name":
                    section_count = db.query(TABLE_MODELS["section"]).count()
                    logger.info(f"   Parent table 'section' has {section_count} records")
                    if section_count == 0:
                        logger.warning(f"   ⚠️  WARNING: 'section' table is empty! 'section_name' table requires section records.")
                
                count = load_csv_to_db(csv_path, model_class, db)
                if count == 0:
                    logger.warning(f"⚠️  WARNING: {table_name} loaded 0 records. Check if CSV file exists and has data.")
                    logger.warning(f"   CSV path: {csv_path}")
                    logger.warning(f"   File size: {file_size} bytes")
                else:
                    logger.info(f"✓ Successfully loaded {count} records into {model_class.__tablename__}")
                total_records += count
            except FileNotFoundError as e:
                logger.error(f"❌ FAILED to load {table_name}: {e}")
                logger.error(f"   CSV path: {csv_path}")
                logger.error(f"   This is a CRITICAL error - the table will be empty!")
                raise
            except Exception as e:
                logger.error(f"❌ FAILED to load {table_name}: {e}")
                logger.error(f"   CSV path: {csv_path}")
                logger.error(f"   Model: {model_class.__name__}, Table: {model_class.__tablename__}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                logger.error(f"   This is a CRITICAL error - the table will be empty!")
                raise

        logger.info(f"\n{'=' * 60}")
        logger.info(f"SUCCESS: Loaded {total_records} total records into database")
        logger.info(f"{'=' * 60}")

    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()