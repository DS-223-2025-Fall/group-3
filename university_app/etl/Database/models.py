"""
Database models for the university ETL schema.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from Database.database import Base, engine

class User(Base):
    """
    Description: Represents a user with login credentials linked to a student.
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(70), nullable=False, unique=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True)


class Student(Base):
    """
    Description: Represents a student and their core attributes in the university system.
    """
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)
    student_name = Column(String(100), nullable=False)
    credit = Column(Integer, nullable=True)
    program_name = Column(String(100), nullable=False)


class Location(Base):
    """
    Description: Represents a physical room or location within the university.
    """
    __tablename__ = "locations"

    room_id = Column(Integer, primary_key=True)
    building_room_name = Column(String(100), nullable=False)


class Instructor(Base):
    """
    Description: Represents an instructor and their assigned office location.
    """
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    bio_url = Column(String(255), nullable=True)
    room_id = Column(Integer, ForeignKey("locations.room_id"), nullable=True)


class Department(Base):
    """Description: Represents an academic department and its main office location."""
    __tablename__ = "departments"

    dept_name = Column(String, primary_key=True)
    roomID = Column(Integer, ForeignKey("locations.room_id"))


class Program(Base):
    """
    Description: Represents an academic program offered by a department.
    """
    __tablename__ = "programs"

    prog_name = Column(String, primary_key=True)
    dept_name = Column(String(50), ForeignKey("departments.dept_name"), nullable=True)


class Course(Base):
    """
    Description: Represents a course with its credits.
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)


class TimeSlot(Base):
    """
    Description: Represents a time slot with day, start/end times, year, and semester.
    """
    __tablename__ = "time_slots"

    time_slot_id = Column(Integer, primary_key=True)
    day_of_week = Column(String(3), nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)


class Section(Base):
    """
    Description: Represents a specific course section in a time slot (which includes year and semester).
    """
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    capacity = Column(Integer, nullable=False)
    roomID = Column(Integer, ForeignKey("locations.room_id"), nullable=False)
    duration = Column(String(50), nullable=True)
    time_slot_id = Column(Integer, ForeignKey("time_slots.time_slot_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=False)
    syllabus_url = Column(String(255), nullable=True)


class SectionName(Base):
    """
    Description: Represents section names/letters linked to sections.
    """
    __tablename__ = "section_name"
    
    section_name = Column(String, primary_key=True)  # section_letter
    section_id = Column(Integer, ForeignKey("sections.id"), primary_key=True, nullable=False)


class Prerequisites(Base):
    """Description: Junction table linking a course to its prerequisite courses."""
    __tablename__ = "prerequisites"

    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)


class Takes(Base):
    """Description: Junction table storing which student takes which section and their status/grade."""
    __tablename__ = "takes"

    student_id = Column(
        Integer, ForeignKey("students.student_id"), primary_key=True
    )
    section_id = Column(Integer, ForeignKey("sections.id"), primary_key=True)
    status = Column(String(20))  # e.g., 'enrolled', 'completed', 'dropped'
    grade = Column(String(5), nullable=True)  # e.g., 'A', 'B+', 'F', 'P', 'NP'


class Works(Base):
    """Description: Junction table storing which instructor works in which department."""
    __tablename__ = "works"

    instructorid = Column(Integer, ForeignKey("instructors.id"), primary_key=True)
    dept_name = Column(String, ForeignKey("departments.dept_name"), primary_key=True)


class HasCourse(Base):
    """Description: Junction table linking programs to the courses they include."""
    __tablename__ = "hascourse"

    prog_name = Column(String, ForeignKey("programs.prog_name"), primary_key=True)
    courseid = Column(Integer, ForeignKey("courses.id"), primary_key=True)


class Cluster(Base):
    """
    Description: Represents an academic cluster (thematic groupings of courses).
    """
    __tablename__ = "clusters"

    cluster_id = Column(Integer, primary_key=True)
    cluster_number = Column(Integer, nullable=True)
    theme = Column(String(500), nullable=True)


class CourseCluster(Base):
    """Description: Junction table linking courses to clusters (many-to-many)."""
    __tablename__ = "course_cluster"

    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    cluster_id = Column(Integer, ForeignKey("clusters.cluster_id"), primary_key=True)


class Preferred(Base):
    """Description: Represents a student's preferred courses."""
    __tablename__ = "preferred"

    student_id = Column(
        Integer, ForeignKey("students.student_id"), primary_key=True
    )
    course_id = Column(
        Integer, ForeignKey("courses.id"), primary_key=True
    )


class DraftSchedule(Base):
    """
    Database model for draft schedules created by students.
    
    Stores draft schedule metadata. The actual sections in each schedule
    are stored in the draft_schedule_sections junction table.
    """
    __tablename__ = "draft_schedules"
    
    draft_schedule_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DraftScheduleSection(Base):
    """
    Database model for draft_schedule_sections junction table.
    
    Links draft schedules to sections (many-to-many relationship).
    """
    __tablename__ = "draft_schedule_sections"
    
    draft_schedule_id = Column(Integer, ForeignKey("draft_schedules.draft_schedule_id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)


class RecommendationResult(Base):
    """
    Database model for storing semester recommendation results from the notebook.
    Matches API model structure for compatibility.
    """
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    recommended_section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    time_slot = Column(Integer, ForeignKey("time_slots.time_slot_id"), nullable=True)
    
    course_name = Column(String(200), nullable=True)
    cluster = Column(String(200), nullable=True)
    credits = Column(Integer, nullable=True)
    
    # Recommendation logic
    recommendation_score = Column(String(50), nullable=True)
    why_recommended = Column(String(1000), nullable=True)
    slot_number = Column(Integer, nullable=True)
    
    # Model and context
    model_version = Column(String(50), nullable=True)
    time_preference = Column(String(20), nullable=True)
    semester = Column(String(20), nullable=True)
    year = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def check_schema_version():
    """
    Check if database schema matches current models.
    Returns True if schema is up to date, False if recreation needed.
    """
    from sqlalchemy import text, inspect
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Define expected schema for critical tables
        schema_checks = {
            'clusters': ['cluster_id', 'cluster_number', 'theme'],
            'users': ['user_id', 'username', 'password', 'student_id'],
            'students': ['student_id', 'student_name', 'credit', 'program_name'],
            'sections': ['id', 'capacity', 'roomID', 'duration', 'time_slot_id', 'course_id', 'instructor_id', 'syllabus_url'],
            'draft_schedules': ['draft_schedule_id', 'student_id', 'name', 'created_at', 'updated_at'],
            'draft_schedule_sections': ['draft_schedule_id', 'section_id'],
        }
        
        for table_name, expected_columns in schema_checks.items():
            if table_name in existing_tables:
                actual_columns = [col['name'] for col in inspector.get_columns(table_name)]
                # Check if all expected columns exist
                missing_columns = [col for col in expected_columns if col not in actual_columns]
                if missing_columns:
                    print(f"⚠️  Schema mismatch in '{table_name}': missing columns {missing_columns}")
                    return False
        
        # Check for old 'user' table (reserved word issue)
        if 'user' in existing_tables:
            print("⚠️  Found old 'user' table (PostgreSQL reserved word)")
            return False
            
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check schema version: {e}")
        return False  # Assume recreation needed on error


def drop_all_tables():
    """
    Drop all tables in the database. Used for clean recreation.
    """
    from sqlalchemy import text, inspect
    
    print("⚠️  Dropping all existing tables for clean recreation...")
    
    try:
        with engine.connect() as connection:
            # Disable foreign key checks temporarily
            connection.execute(text("SET session_replication_role = 'replica';"))
            
            # Drop all tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            for table in tables:
                print(f"   Dropping table: {table}")
                connection.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            # Re-enable foreign key checks
            connection.execute(text("SET session_replication_role = 'origin';"))
            connection.commit()
            
        print("✓ All tables dropped successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False


def create_tables():
    """
    Description: Creates all database tables defined by the ORM models for ETL/testing.
    Automatically detects schema mismatches and recreates tables if needed.
    inputs: None.
    return: None. The function issues CREATE TABLE statements via SQLAlchemy metadata.
    """
    from sqlalchemy import text, inspect
    
    print("=" * 60)
    print("Checking database schema...")
    print("=" * 60)
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # If no tables exist, just create them
    if not existing_tables:
        print("No existing tables found. Creating fresh database...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return
    
    # Check if schema matches current models
    schema_ok = check_schema_version()
    
    if not schema_ok:
        print("\n⚠️  Schema mismatch detected. Recreating all tables with correct schema...")
        print("   This will delete all existing data and reload from CSV files.")
        
        # Drop all tables
        if drop_all_tables():
            # Create tables with correct schema
            Base.metadata.create_all(bind=engine)
            print("✅ All tables recreated with correct schema")
        else:
            print("❌ Failed to drop tables. Attempting to create missing tables...")
            Base.metadata.create_all(bind=engine)
    else:
        # Schema is fine, just create any missing tables
        print("✅ Schema is up to date. Creating any missing tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified")
    
    print("=" * 60)
