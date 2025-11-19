"""
Database Models for the University Course Management System.

This module defines the database models using SQLAlchemy for students, instructors and #TODO: add later

Modules:
    - sqlalchemy: For ORM and database schema definition.
    - pydantic: For data validation (not used in these models).
"""

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
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
   