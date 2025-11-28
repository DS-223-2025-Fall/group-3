"""
Database helper methods for University Course Management System.
Provides reusable database utility functions for common CRUD operations to reduce code duplication across endpoints.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, TypeVar, Dict, Any, Optional, List
from fastapi import HTTPException

# Generic type for SQLAlchemy models
ModelType = TypeVar('ModelType')


def get_by_id(
    db: Session,
    model: Type[ModelType],
    **filters
) -> Optional[ModelType]:
    """
    Get a single record by ID or other filters from the database.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        **filters: Keyword arguments for filtering (e.g., student_id=1).
    
    Return:
        Optional[ModelType]: Model instance or None if not found.
    """
    try:
        return db.query(model).filter_by(**filters).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_all(
    db: Session,
    model: Type[ModelType],
    skip: int = 0,
    limit: int = 100,
    **filters
) -> List[ModelType]:
    """
    Get all records with optional filtering and pagination from the database.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        skip (int): Number of records to skip (for pagination), default 0.
        limit (int): Maximum number of records to return, default 100.
        **filters: Optional keyword arguments for filtering.
    
    Return:
        List[ModelType]: List of model instances.
    """
    try:
        query = db.query(model)
        
        # Apply filters
        if filters:
            query = query.filter_by(**filters)
        
        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def create_record(
    db: Session,
    model: Type[ModelType],
    data: Dict[str, Any]
) -> ModelType:
    """
    Create a new database record with the provided data.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        data (Dict[str, Any]): Dictionary of field names and values.
    
    Return:
        ModelType: Created model instance.
    
    Raises:
        HTTPException: If creation fails.
    """
    try:
        db_record = model(**data)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")


def update_record(
    db: Session,
    model: Type[ModelType],
    data: Dict[str, Any],
    **filters
) -> Optional[ModelType]:
    """
    Update an existing database record with new values.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        data (Dict[str, Any]): Dictionary of field names and new values.
        **filters: Keyword arguments to identify the record (e.g., student_id=1).
    
    Return:
        Optional[ModelType]: Updated model instance or None if not found.
    
    Raises:
        HTTPException: If update fails or record not found.
    """
    try:
        record = db.query(model).filter_by(**filters).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        db.commit()
        db.refresh(record)
        return record
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")


def delete_record(
    db: Session,
    model: Type[ModelType],
    **filters
) -> bool:
    """
    Delete a database record matching the provided filters.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        **filters: Keyword arguments to identify the record (e.g., student_id=1).
    
    Return:
        bool: True if deleted, False if not found.
    
    Raises:
        HTTPException: If deletion fails.
    """
    try:
        record = db.query(model).filter_by(**filters).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        
        db.delete(record)
        db.commit()
        return True
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def count_records(
    db: Session,
    model: Type[ModelType],
    **filters
) -> int:
    """
    Count records matching the given filters in the database.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        **filters: Optional keyword arguments for filtering.
    
    Return:
        int: Number of matching records.
    """
    try:
        query = db.query(model)
        if filters:
            query = query.filter_by(**filters)
        return query.count()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def exists(
    db: Session,
    model: Type[ModelType],
    **filters
) -> bool:
    """
    Check if a record exists in the database matching the provided filters.
    
    Input:
        db (Session): Database session.
        model (Type[ModelType]): SQLAlchemy model class.
        **filters: Keyword arguments for filtering.
    
    Return:
        bool: True if record exists, False otherwise.
    """
    try:
        return db.query(model).filter_by(**filters).first() is not None
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

