"""
Helper functions for loading data and generating recommendations
"""

import pandas as pd
import os
from typing import Dict
from datetime import datetime
from .semester_scheduler import SemesterScheduler


def load_data_from_db(engine, current_year: int = None, current_semester: str = None) -> Dict:
    """
    Description:
        Load all necessary data from database into pandas DataFrames.
    
    Input:
        engine: SQLAlchemy engine
        current_year (int, optional): Current academic year. Defaults to CURRENT_YEAR env var or current year.
        current_semester (str, optional): Current semester ('Fall', 'Spring', 'Summer'). Defaults to DEFAULT_SEMESTER env var or 'Fall'.
    
    Output:
        Dict: Dictionary of DataFrames with keys: students, courses, sections, etc.
    """
    # Use defaults from environment or datetime if not provided
    if current_year is None:
        current_year = int(os.environ.get('CURRENT_YEAR', datetime.now().year))
    if current_semester is None:
        current_semester = os.environ.get('DEFAULT_SEMESTER', 'Fall')
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
    current_year: int = None,
    current_semester: str = None
) -> list:
    """
    Description:
        Generate recommendations for a single student.
    
    Input:
        engine: SQLAlchemy engine
        student_id (int): Student ID to generate recommendations for
        time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
        current_year (int, optional): Current academic year. Defaults to CURRENT_YEAR env var or current year.
        current_semester (str, optional): Current semester. Defaults to DEFAULT_SEMESTER env var or 'Fall'.
    
    Output:
        list: List of recommendation dictionaries
    """
    # Load data (will use defaults from environment if not provided)
    data = load_data_from_db(engine, current_year, current_semester)
    
    # Initialize scheduler
    scheduler = SemesterScheduler(data, current_year=current_year, current_semester=current_semester)
    
    # Generate recommendations
    recommendations = scheduler.recommend_semester(student_id, time_preference=time_preference)
    
    return recommendations

