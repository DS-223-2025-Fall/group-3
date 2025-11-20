"""
Database Helper Methods for Notebook (Data Science).

This module provides reusable database utility functions for common CRUD operations.
Adapted from API db_helpers but without HTTPException (for notebook use).

Usage:
    from Database.db_helpers import get_by_id, create_record, update_record, delete_record
    
    # Get a student by ID
    student = get_by_id(db, Student, student_id=1)
    
    # Create a new record
    new_student = create_record(db, Student, {"student_name": "John", "credit": 0})
    
    # Update a record
    updated = update_record(db, Student, student_id=1, student_name="Jane")
    
    # Delete a record
    delete_record(db, Student, student_id=1)
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, TypeVar, Dict, Any, Optional, List

# Generic type for SQLAlchemy models
ModelType = TypeVar('ModelType')


def get_by_id(
    db: Session,
    model: Type[ModelType],
    **filters
) -> Optional[ModelType]:
    """
    Get a single record by ID or other filters.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        **filters: Keyword arguments for filtering (e.g., student_id=1)
    
    Returns:
        Model instance or None if not found
    
    Example:
        student = get_by_id(db, Student, student_id=1)
    """
    try:
        return db.query(model).filter_by(**filters).first()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error: {str(e)}")


def get_all(
    db: Session,
    model: Type[ModelType],
    skip: int = 0,
    limit: int = 100,
    **filters
) -> List[ModelType]:
    """
    Get all records with optional filtering and pagination.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        **filters: Optional keyword arguments for filtering
    
    Returns:
        List of model instances
    
    Example:
        students = get_all(db, Student, skip=0, limit=10)
    """
    try:
        query = db.query(model)
        
        # Apply filters
        if filters:
            query = query.filter_by(**filters)
        
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error: {str(e)}")


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
        raise ValueError(f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Invalid data: {str(e)}")


def update_record(
    db: Session,
    model: Type[ModelType],
    data: Dict[str, Any],
    **filters
) -> Optional[ModelType]:
    """
    Update an existing database record.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        data: Dictionary of field names and new values
        **filters: Keyword arguments to identify the record (e.g., student_id=1)
    
    Returns:
        Updated model instance or None if not found
    
    Raises:
        ValueError: If update fails or record not found
    
    Example:
        student = update_record(
            db, Student,
            {"credit": 50},
            student_id=1
        )
    """
    try:
        record = db.query(model).filter_by(**filters).first()
        if not record:
            raise ValueError(f"{model.__name__} not found")
        
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        db.commit()
        db.refresh(record)
        return record
    except ValueError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Invalid data: {str(e)}")


def delete_record(
    db: Session,
    model: Type[ModelType],
    **filters
) -> bool:
    """
    Delete a database record.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        **filters: Keyword arguments to identify the record (e.g., student_id=1)
    
    Returns:
        True if deleted, False if not found
    
    Raises:
        ValueError: If deletion fails
    
    Example:
        deleted = delete_record(db, Student, student_id=1)
    """
    try:
        record = db.query(model).filter_by(**filters).first()
        if not record:
            raise ValueError(f"{model.__name__} not found")
        
        db.delete(record)
        db.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error: {str(e)}")


def count_records(
    db: Session,
    model: Type[ModelType],
    **filters
) -> int:
    """
    Count records matching the given filters.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        **filters: Optional keyword arguments for filtering
    
    Returns:
        Number of matching records
    
    Example:
        total_students = count_records(db, Student)
    """
    try:
        query = db.query(model)
        if filters:
            query = query.filter_by(**filters)
        return query.count()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error: {str(e)}")


def exists(
    db: Session,
    model: Type[ModelType],
    **filters
) -> bool:
    """
    Check if a record exists.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        **filters: Keyword arguments for filtering
    
    Returns:
        True if record exists, False otherwise
    
    Example:
        if exists(db, Student, student_id=1):
            print("Student exists")
    """
    try:
        return db.query(model).filter_by(**filters).first() is not None
    except SQLAlchemyError as e:
        raise ValueError(f"Database error: {str(e)}")

