"""
Helper functions for Streamlit app to interact with FastAPI backend.

This module provides helper functions to fetch data from the existing
FastAPI endpoints. It reuses the same API that the React frontend uses.
"""

import requests
from typing import Optional, List, Dict
import os

# API base URL - defaults to localhost, can be overridden via environment variable
API_BASE_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8008")


def fetch_sections(
    year: Optional[str] = None,
    semester: Optional[str] = None,
    course_type: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict]:
    """
    Fetch course sections from the FastAPI /sections endpoint.
    
    Args:
        year: Filter by year (e.g., "2024")
        semester: Filter by semester (e.g., "Fall", "Spring", "Summer")
        course_type: Filter by course type (e.g., "GenEd", "Major", "Elective")
        search: Search by course name
    
    Returns:
        List of section dictionaries with course details
    
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    params = {}
    if year:
        params["year"] = year
    if semester:
        params["semester"] = semester
    if course_type:
        params["course_type"] = course_type
    if search:
        params["search"] = search
    
    response = requests.get(f"{API_BASE_URL}/sections", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_courses() -> List[Dict]:
    """
    Fetch all courses from the FastAPI /courses endpoint.
    
    Returns:
        List of course dictionaries
    
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    response = requests.get(f"{API_BASE_URL}/courses", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_student(student_id: int) -> Dict:
    """
    Fetch a student by ID from the FastAPI /students/{student_id} endpoint.
    
    Args:
        student_id: Student ID
    
    Returns:
        Student dictionary
    
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    response = requests.get(f"{API_BASE_URL}/students/{student_id}", timeout=10)
    response.raise_for_status()
    return response.json()

