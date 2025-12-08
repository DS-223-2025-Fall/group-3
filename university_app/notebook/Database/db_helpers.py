"""
Database Helper Methods for Notebook (Data Science).

This module provides reusable database utility functions for common CRUD operations.
Adapted from API db_helpers but without HTTPException (for notebook use).

Usage:
    from Database.db_helpers import create_record
    
    # Create a new record
    new_record = create_record(db, RecommendationResult, {...})
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, TypeVar, Dict, Any

# Generic type for SQLAlchemy models
ModelType = TypeVar('ModelType')


def create_record(
    db: Session,
    model: Type[ModelType],
    data: Dict[str, Any]
) -> ModelType:
    """
    Create a new database record.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        data: Dictionary of field names and values
    
    Returns:
        Created model instance
    
    Raises:
        ValueError: If creation fails
    
    Example:
        student = create_record(db, Student, {
            "student_name": "John Doe",
            "credit": 0
        })
    """
    try:
        db_record = model(**data)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except SQLAlchemyError as e:
        db.rollback()
        # Use SQLAlchemyError for database-specific errors
        raise SQLAlchemyError(f"Database error: {str(e)}") from e
    except Exception as e:
        db.rollback()
        # Use ValueError for validation/input errors
        raise ValueError(f"Invalid data: {str(e)}") from e

