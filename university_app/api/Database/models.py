"""
Database Models for the ETL Process.

This module defines the database models using SQLAlchemy for employees, customers, and products.

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
   To do later
    """
    pass
   