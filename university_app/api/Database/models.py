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
    Description:
        Represents a student record in the database.
    Inputs:
        No direct inputs; SQLAlchemy handles the attributes.
    Return:
        Creates a database table storing student IDs, names, and credits.
    """

    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    credit = Column(Integer, default=0)


# Section model (minimal for TakesDB foreign key)
class SectionDB(Base):
    """
    Description:
        Represents a course section in the system.
    Inputs:
        Managed automatically by SQLAlchemy; only stores the section ID.
    Return:
        Creates a minimal sections table for foreign key relationships.
    """

    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)


class TakesDB(Base):
    """
    Description:
        Stores the relationship between students and sections they take.
    Inputs:
        Student ID, section ID, enrollment status, and optional grade.
    Return:
        Creates a table tracking enrollments and grades for each student-section pair.
    """
    
    __tablename__ = "takes"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    status = Column(String(20))  # e.g., 'enrolled', 'completed', 'dropped'
    grade = Column(String(5), nullable=True)  # e.g., 'A', 'B+', 'F', 'P', 'NP'