"""
Database models for the university ETL schema.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
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
    )  # Fixed to match actual schema
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


def create_tables():
    """
    Description: Creates all database tables defined by the ORM models for ETL/testing.
    inputs: None.
    return: None. The function issues CREATE TABLE statements via SQLAlchemy metadata.
    """
    Base.metadata.create_all(bind=engine)
