"""
Database Models for University ETL.

These models define the complete database schema for the university system.
The ETL process can use these models to:
1. Create database tables
2. Load CSV data into the database
3. Validate data structure

Note: The data generator creates dictionaries that are saved to CSV files,
but these models allow the ETL developer to test database loading independently.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from Database.database import Base, engine


class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True)  # Matches API schema
    student_name = Column(String)  # Matches API schema
    credit = Column(Integer)


class Location(Base):
    __tablename__ = "locations"
    
    room_id = Column(Integer, primary_key=True)
    building_room_name = Column(String)


class Instructor(Base):
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    bio_url = Column(String) 
    room_id = Column(Integer, ForeignKey('locations.room_id'))


class Department(Base):
    __tablename__ = "departments"
    
    dept_name = Column(String, primary_key=True)
    roomID = Column(Integer, ForeignKey('locations.room_id'))


class Program(Base):
    __tablename__ = "programs"
    
    prog_name = Column(String, primary_key=True)
    deptID = Column(String, ForeignKey('departments.dept_name'))  # Matches CSV field name
    student_id = Column(Integer, ForeignKey('students.student_id'))  # Fixed to match actual schema  


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    credits = Column(Integer)
    cluster_number = Column(String, nullable=True)  # Comma-separated string for multiple clusters (e.g., "1,2,3,4,6")


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    time_slot_id = Column(Integer, primary_key=True)
    day_of_week = Column(String)
    start_time = Column(String)
    end_time = Column(String)


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer)
    roomID = Column(Integer, ForeignKey('locations.room_id'))
    duration = Column(String)
    year = Column(Integer)
    time_slot_id = Column(Integer, ForeignKey('time_slots.time_slot_id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    syllabus_url = Column(String)


# Junction Tables
class Prerequisites(Base):
    __tablename__ = "prerequisites"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class Takes(Base):
    __tablename__ = "takes"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)  # Fixed to match actual schema
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    status = Column(String(20))  # e.g., 'enrolled', 'completed', 'dropped'
    grade = Column(String(5), nullable=True)  # e.g., 'A', 'B+', 'F', 'P', 'NP'


class Works(Base):
    __tablename__ = "works"
    
    instructorid = Column(Integer, ForeignKey('instructors.id'), primary_key=True) 
    dept_name = Column(String, ForeignKey('departments.dept_name'), primary_key=True)


class HasCourse(Base):
    __tablename__ = "hascourse"
    
    prog_name = Column(String, ForeignKey('programs.prog_name'), primary_key=True)
    courseid = Column(Integer, ForeignKey('courses.id'), primary_key=True)  


# Function to create all tables (useful for ETL testing)
def create_tables():
    """Create all database tables. Useful for ETL developer to test database loading."""
    Base.metadata.create_all(bind=engine)
