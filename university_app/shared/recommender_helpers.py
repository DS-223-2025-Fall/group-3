"""
Helper functions for loading data and generating recommendations
"""

import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Optional
from .semester_scheduler import SemesterScheduler


def load_data_from_db(engine, current_year: int = 2025, current_semester: str = 'Fall') -> Dict:
    """
    Load all necessary data from database into pandas DataFrames.
    
    Args:
        engine: SQLAlchemy engine
        current_year: Current academic year
        current_semester: Current semester ('Fall', 'Spring', 'Summer')
    
    Returns:
        Dictionary of DataFrames with keys: students, courses, sections, etc.
    """
    data = {}
    
    # Load required tables
    data['students'] = pd.read_sql_table('students', engine)
    data['courses'] = pd.read_sql_table('courses', engine)
    data['sections'] = pd.read_sql_table('sections', engine)
    data['takes'] = pd.read_sql_table('takes', engine)
    data['prerequisites'] = pd.read_sql_table('prerequisites', engine)
    data['time_slots'] = pd.read_sql_table('time_slots', engine)
    data['programs'] = pd.read_sql_table('programs', engine)
    data['hascourse'] = pd.read_sql_table('hascourse', engine)
    
    # Load optional tables
    try:
        data['clusters'] = pd.read_sql_table('clusters', engine)
    except:
        data['clusters'] = pd.DataFrame()
    
    try:
        data['course_cluster'] = pd.read_sql_table('course_cluster', engine)
    except:
        data['course_cluster'] = pd.DataFrame()
    
    try:
        data['preferred'] = pd.read_sql_table('preferred', engine)
    except:
        data['preferred'] = pd.DataFrame()
    
    return data


def generate_recommendations_for_student(
    engine,
    student_id: int,
    time_preference: str = 'any',
    current_year: int = 2025,
    current_semester: str = 'Fall'
) -> list:
    """
    Generate recommendations for a single student.
    
    Args:
        engine: SQLAlchemy engine
        student_id: Student ID to generate recommendations for
        time_preference: Time preference ('morning', 'afternoon', 'evening', 'any')
        current_year: Current academic year
        current_semester: Current semester
    
    Returns:
        List of recommendation dictionaries
    """
    # Load data
    data = load_data_from_db(engine, current_year, current_semester)
    
    # Initialize scheduler
    scheduler = SemesterScheduler(data, current_year=current_year, current_semester=current_semester)
    
    # Generate recommendations
    recommendations = scheduler.recommend_semester(student_id, time_preference=time_preference)
    
    return recommendations

