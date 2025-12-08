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
import sys
from sqlalchemy import text, inspect
from Database.database import engine, get_db
from Database.models import (
    User, Student, Location, Instructor, Department, Program, Course,
    TimeSlot, Section, SectionName, Prerequisites, Takes, Works, HasCourse,
    Cluster, CourseCluster, Preferred, RecommendationResult,
    create_tables
)

# Add shared module to path for recommendation generation
# Try multiple paths: Docker mount (/shared) and local development (../shared)
shared_paths = [
    '/shared',  # Docker mount
    os.path.join(os.path.dirname(__file__), '..', 'shared'),  # Local development
]

shared_found = False
for path in shared_paths:
    if os.path.exists(path) and os.path.exists(os.path.join(path, '__init__.py')):
        sys.path.insert(0, os.path.dirname(path) if path != '/shared' else '/')
        shared_found = True
        break

try:
    from recommender_helpers import generate_recommendations_for_student
    RECOMMENDER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Shared recommender module not available: {e}")
    logger.warning("Recommendations will not be auto-generated, but students can still generate them via the frontend.")
    RECOMMENDER_AVAILABLE = False

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
    Description:
        Load a single CSV file into the corresponding database table using the given model.
    
    Input:
        csv_path (str): Path to the CSV file
        model_class: SQLAlchemy model class
        db_session: SQLAlchemy Session
    
    Output:
        int: Number of records inserted into the table
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
    Description:
        Create tables if needed and load all CSVs into the database in dependency order.
    Clears existing data first to avoid duplicates, then loads fresh data.
    
    Input:
        None (uses global LOAD_ORDER and TABLE_MODELS)
    
    Output:
        None
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
        
        db.commit()
        
        # Now clear all ETL tables in reverse dependency order to avoid foreign key constraints
        # Use raw SQL DELETE to avoid ORM schema mismatches (e.g., clusters.theme column issue)
        logger.info("Clearing existing data from ETL tables (in reverse dependency order)...")
        
        # First, rollback any existing failed transaction
        try:
            db.rollback()
        except:
            pass
        
        for table_name in reversed(LOAD_ORDER):
            model_class = TABLE_MODELS[table_name]
            table_name_db = model_class.__tablename__
            
            try:
                # Check if table exists
                inspector = inspect(db.bind)
                table_names = inspector.get_table_names()
                
                if table_name_db not in table_names:
                    logger.debug(f"Table {table_name_db} does not exist yet, skipping clear")
                    continue
                
                # Use raw SQL DELETE to avoid ORM schema mismatches
                # This bypasses any column mismatch issues (e.g., missing theme column in clusters)
                try:
                    # Start a savepoint for this table's operation
                    db.begin_nested()
                    result = db.execute(text(f'DELETE FROM "{table_name_db}"'))
                    deleted_count = result.rowcount
                    db.commit()  # Commit the nested transaction
                    
                    if deleted_count > 0:
                        logger.info(f"Cleared {deleted_count} records from {table_name} ({table_name_db})")
                    else:
                        logger.debug(f"Table {table_name} ({table_name_db}) is already empty")
                except Exception as delete_error:
                    # Rollback the nested transaction and continue
                    db.rollback()
                    logger.warning(f"Could not clear {table_name} ({table_name_db}): {delete_error}. Continuing...")
                    continue
                        
            except Exception as e:
                logger.warning(f"Error checking/clearing {table_name} ({table_name_db}): {e}. Continuing...")
                try:
                    db.rollback()
                except:
                    pass
                continue
        
        # Final commit for any remaining operations
        try:
            db.commit()
            logger.info("All existing data cleared. Loading fresh data...")
        except Exception as e:
            logger.warning(f"Error in final commit: {e}. Rolling back...")
            db.rollback()

        # Now load tables in dependency order
        data_dir = "data"
        total_records = 0
        failed_tables = []
        successful_tables = []

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
                    failed_tables.append(table_name)
                    continue  # Don't raise, continue to next table
                
                # Check if CSV file is empty
                file_size = os.path.getsize(csv_path)
                if file_size == 0:
                    error_msg = f"CSV file is empty: {csv_path}"
                    logger.error(f"❌ {error_msg}")
                    failed_tables.append(table_name)
                    continue  # Don't raise, continue to next table
                
                logger.info(f"   CSV file found ({file_size} bytes)")
                
                # Verify parent tables exist for foreign key dependencies
                if table_name == "users":
                    try:
                        student_count = db.query(TABLE_MODELS["student"]).count()
                        logger.info(f"   Parent table 'student' has {student_count} records")
                        if student_count == 0:
                            logger.warning(f"   ⚠️  WARNING: 'student' table is empty! 'users' table requires student records.")
                    except Exception as e:
                        logger.warning(f"   Could not check parent table: {e}")
                elif table_name == "section_name":
                    try:
                        section_count = db.query(TABLE_MODELS["section"]).count()
                        logger.info(f"   Parent table 'section' has {section_count} records")
                        if section_count == 0:
                            logger.warning(f"   ⚠️  WARNING: 'section' table is empty! 'section_name' table requires section records.")
                    except Exception as e:
                        logger.warning(f"   Could not check parent table: {e}")
                
                count = load_csv_to_db(csv_path, model_class, db)
                if count == 0:
                    logger.warning(f"⚠️  WARNING: {table_name} loaded 0 records. Check if CSV file exists and has data.")
                    logger.warning(f"   CSV path: {csv_path}")
                    logger.warning(f"   File size: {file_size} bytes")
                    failed_tables.append(table_name)
                else:
                    logger.info(f"✓ Successfully loaded {count} records into {model_class.__tablename__}")
                    successful_tables.append(table_name)
                total_records += count
            except Exception as e:
                logger.error(f"❌ FAILED to load {table_name}: {e}")
                logger.error(f"   CSV path: {csv_path}")
                logger.error(f"   Model: {model_class.__name__}, Table: {model_class.__tablename__}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                logger.error(f"   Continuing to next table...")
                failed_tables.append(table_name)
                # Rollback failed transaction and continue
                try:
                    db.rollback()
                except:
                    pass
                continue  # Don't raise, continue to next table

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Data Loading Summary:")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total records loaded: {total_records}")
        logger.info(f"Successful tables: {len(successful_tables)}/{len(LOAD_ORDER)}")
        logger.info(f"Failed tables: {len(failed_tables)}/{len(LOAD_ORDER)}")
        
        if successful_tables:
            logger.info(f"\n✅ Successfully loaded tables:")
            for table in successful_tables:
                logger.info(f"   - {table}")
        
        if failed_tables:
            logger.warning(f"\n❌ Failed tables:")
            for table in failed_tables:
                logger.warning(f"   - {table}")
            logger.warning(f"\nTo fix: docker compose down -v && docker compose up -d")
            # Exit with error code if critical tables failed
            critical_tables = ["location", "student", "instructor", "course", "section"]
            failed_critical = [t for t in failed_tables if t in critical_tables]
            if failed_critical:
                logger.error(f"\n❌ CRITICAL tables failed: {failed_critical}")
                logger.error(f"Database is incomplete and may not function properly!")
                raise Exception(f"Critical tables failed to load: {failed_critical}")
        else:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"✅ SUCCESS: All tables loaded successfully!")
            logger.info(f"{'=' * 60}")
            
            # Automatically generate recommendations for all students
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Generating recommendations for all students...")
            logger.info(f"{'=' * 60}")
            try:
                generate_recommendations_for_all_students(db)
                logger.info(f"✅ Recommendations generated successfully!")
            except Exception as e:
                logger.warning(f"⚠️  Could not generate recommendations: {e}")
                logger.warning(f"   Students can still generate recommendations via the frontend")
                # Don't fail the ETL process if recommendations fail

    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        try:
            db.rollback()
        except:
            pass
        raise
    finally:
        db.close()


def generate_recommendations_for_all_students(db_session):
    """
    Description:
    Generate recommendations for all students in the database.
    Uses default 'any' time preference.
    
    Input:
        db_session: SQLAlchemy database session
    
    Output:
        None
    """
    if not RECOMMENDER_AVAILABLE:
        logger.warning("Recommender not available, skipping recommendation generation")
        return
    
    try:
        # Get all students
        students = db_session.query(Student).all()
        if not students:
            logger.info("No students found, skipping recommendation generation")
            return
        
        logger.info(f"Generating recommendations for {len(students)} students...")
        
        # Generate recommendations for each student
        total_generated = 0
        for student in students:
            try:
                recommendations = generate_recommendations_for_student(
                    engine=engine,
                    student_id=student.student_id,
                    time_preference='any',  # Default to 'any'
                    current_year=2025,
                    current_semester='Fall'
                )
                
                if not recommendations:
                    logger.debug(f"No recommendations for student {student.student_id}")
                    continue
                
                # Save recommendations to database
                for slot_num, rec in enumerate(recommendations, 1):
                    # Get time_slot_id from section
                    section = db_session.query(Section).filter(Section.id == int(rec['section_id'])).first()
                    time_slot_id = section.time_slot_id if section else None
                    
                    # Convert why_recommended list to string
                    why_recommended_str = ', '.join(rec.get('why_recommended', []))
                    
                    result_data = {
                        'student_id': student.student_id,
                        'course_id': int(rec['course_id']),
                        'recommended_section_id': int(rec['section_id']),
                        'course_name': rec['course_name'],
                        'cluster': rec.get('cluster', ''),
                        'credits': int(rec.get('credits', 0)),
                        'time_slot': int(time_slot_id) if time_slot_id is not None else None,
                        'recommendation_score': str(rec.get('score', '1.0')),
                        'why_recommended': why_recommended_str,
                        'slot_number': slot_num,
                        'model_version': 'semester_scheduler_v1',
                        'time_preference': 'any',
                        'semester': 'Fall',
                        'year': 2025
                    }
                    
                    recommendation = RecommendationResult(**result_data)
                    db_session.add(recommendation)
                    total_generated += 1
                
                # Commit after each student to avoid large transactions
                db_session.commit()
                
            except Exception as e:
                logger.warning(f"Failed to generate recommendations for student {student.student_id}: {e}")
                db_session.rollback()
                continue
        
        logger.info(f"✅ Generated {total_generated} recommendations for {len(students)} students")
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        db_session.rollback()
        raise


if __name__ == "__main__":
    main()