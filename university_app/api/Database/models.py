"""
Database Models for the University Course Management System.

This module defines the database models using SQLAlchemy for the complete university system.
All models must be imported here so they are registered with SQLAlchemy's Base metadata
and tables are created when the API service starts.

Modules:
    - sqlalchemy: For ORM and database schema definition.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from Database.database import Base

# Database Models

class StudentDB(Base):
    """
    Database model for Student table.
    
    Attributes:
        student_id: Primary key, auto-incrementing integer
        student_name: Student's name
        credit: Number of credits the student has
    """
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    credit = Column(Integer, default=0)


class LocationDB(Base):
    """Database model for Location table."""
    __tablename__ = "locations"
    
    room_id = Column(Integer, primary_key=True)
    building_room_name = Column(String)


class InstructorDB(Base):
    """Database model for Instructor table."""
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    bio_url = Column(String) 
    room_id = Column(Integer, ForeignKey('locations.room_id'))


class DepartmentDB(Base):
    """Database model for Department table."""
    __tablename__ = "departments"
    
    dept_name = Column(String, primary_key=True)
    roomID = Column(Integer, ForeignKey('locations.room_id'))


class ProgramDB(Base):
    """Database model for Program table."""
    __tablename__ = "programs"
    
    prog_name = Column(String, primary_key=True)
    deptID = Column(String, ForeignKey('departments.dept_name'))
    student_id = Column(Integer, ForeignKey('students.student_id'))


class CourseDB(Base):
    """Database model for Course table."""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    credits = Column(Integer)
    cluster_number = Column(String, nullable=True)  


class TimeSlotDB(Base):
    """Database model for TimeSlot table."""
    __tablename__ = "time_slots"
    
    time_slot_id = Column(Integer, primary_key=True)
    day_of_week = Column(String)
    start_time = Column(String)
    end_time = Column(String)


class SectionDB(Base):
    """Database model for Section table."""
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


class PrerequisitesDB(Base):
    """Database model for Prerequisites table (junction table)."""
    __tablename__ = "prerequisites"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class TakesDB(Base):
    """
    Database model for Takes table (student enrollments).
    
    Attributes:
        student_id: Foreign key to students table (part of primary key)
        section_id: Foreign key to sections table (part of primary key)
        status: Enrollment status (e.g., 'enrolled', 'completed', 'dropped')
        grade: Grade received (e.g., 'A', 'B+', 'F', 'P', 'NP') or None
    """
    __tablename__ = "takes"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    status = Column(String(20))  # e.g., 'enrolled', 'completed', 'dropped'
    grade = Column(String(5), nullable=True)  # e.g., 'A', 'B+', 'F', 'P', 'NP'


class WorksDB(Base):
    """Database model for Works table (junction table: instructor-department)."""
    __tablename__ = "works"
    
    instructorid = Column(Integer, ForeignKey('instructors.id'), primary_key=True) 
    dept_name = Column(String, ForeignKey('departments.dept_name'), primary_key=True)


class HasCourseDB(Base):
    """Database model for HasCourse table (junction table: program-course)."""
    __tablename__ = "hascourse"
    
    prog_name = Column(String, ForeignKey('programs.prog_name'), primary_key=True)
    courseid = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class ClusterDB(Base):
    """
    Database model for Cluster table - weak entity (depends on Program).
    Represents academic clusters within programs.
    """
    __tablename__ = "clusters"
    
    cluster_id = Column(Integer, primary_key=True)
    cluster_number = Column(Integer, nullable=False)  # e.g., 1, 2, 3, 4, 5, 6, 7, 8, 9
    prog_name = Column(String, ForeignKey('programs.prog_name'), nullable=False)  # Weak entity dependency
    description = Column(String, nullable=True)  # Optional description of the cluster


class CourseClusterDB(Base):
    """
    Database model for Course-Cluster junction table (many-to-many relationship).
    Links courses to clusters.
    """
    __tablename__ = "course_cluster"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    cluster_id = Column(Integer, ForeignKey('clusters.cluster_id'), primary_key=True)


class PreferredDB(Base):
    """
    Database model for Preferred table - weak entity (depends on Student and Cluster).
    Represents student preferences for clusters.
    """
    __tablename__ = "preferred"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)  # Weak entity dependency
    cluster_id = Column(Integer, ForeignKey('clusters.cluster_id'), primary_key=True)  # Weak entity dependency
    preference_order = Column(Integer, nullable=True)  # Optional: order of preference (1 = highest)