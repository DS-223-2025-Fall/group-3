"""
Database Models for the University Course Management System.

This module defines the database models using SQLAlchemy for students, instructors and #TODO: add later

Modules:
    - sqlalchemy: For ORM and database schema definition.
    - pydantic: For data validation (not used in these models).
"""

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

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


# Section model (minimal for TakesDB foreign key)
class SectionDB(Base):
    """Minimal Section model for foreign key reference."""
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)


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