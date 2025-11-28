# Import all models so they are registered with SQLAlchemy Base metadata
# This ensures all tables are created when Base.metadata.create_all() is called
from Database.models import (
    StudentDB, SectionDB, TakesDB, LocationDB, InstructorDB, 
    DepartmentDB, ProgramDB, CourseDB, TimeSlotDB, PrerequisitesDB, 
    WorksDB, HasCourseDB, ClusterDB, CourseClusterDB, PreferredDB,
    RecommendationResultDB, ABTestAssignmentDB, UIElementClickDB, Base
)
from Database.schema import (
    Student, StudentCreate,
    Location, LocationCreate,
    Instructor, InstructorCreate,
    Department, DepartmentCreate,
    Program, ProgramCreate,
    Course, CourseCreate,
    TimeSlot, TimeSlotCreate,
    Section, SectionCreate,
    Prerequisites, PrerequisitesCreate,
    Takes, TakesCreate,
    Works, WorksCreate,
    HasCourse, HasCourseCreate,
    Cluster, ClusterCreate,
    CourseCluster, CourseClusterCreate,
    Preferred, PreferredCreate,
    UIElementPosition, UIElementClick, UIElementClickCreate
)
from Database.database import get_db, engine
from Database.init_db import ensure_database_initialized

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from datetime import datetime
from typing import Optional

app = FastAPI(title="University Course Management API")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for syllabi
# Syllabi are stored in /api/syllabi/ in the container (mounted from ./syllabi on host)
SYLLABI_DIR = "/api/syllabi"
if os.path.exists(SYLLABI_DIR):
    app.mount("/syllabi", StaticFiles(directory=SYLLABI_DIR), name="syllabi")


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup.
    Creates tables and loads data if database is empty.
    """
    ensure_database_initialized()

# STUDENT ENDPOINTS

# GET Request - Retrieve a student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a student by their unique ID.

    Args:
        student_id (int): The unique identifier of the student.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Student: The student's details.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# POST Request - Create a new student
@app.post("/students/", response_model=Student)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student.

    Args:
        student (StudentCreate): The student data to create.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Student: The newly created student's details.
    """
    db_student = StudentDB(
        student_name=student.student_name,
        credit=student.credit,
        program_name=student.program_name
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# PUT - Update a student

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, updated_student: StudentCreate, db: Session = Depends(get_db)):
    """
    Update an existing student's details.

    Args:
        student_id (int): The unique identifier of the student to update.
        updated_student (StudentCreate): The new student data.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Student: The updated student's details.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in updated_student.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


# DELETE - Delete a student by id

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student by their unique ID.

    Args:
        student_id (int): The unique identifier of the student to delete.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        dict: A message confirming successful deletion.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

#TODO: add others as well

# UI ELEMENT AB TESTING ENDPOINTS

# Define UI element position variants for A/B testing
UI_POSITION_VARIANTS = {
    'A': {
        'search_bar': 'top',
        'dropdowns': 'left',
        'buttons': 'right',
        'header_color': '#1e3a5f',  # Original blue
        'search_button_position': 'inline'
    },
    'B': {
        'search_bar': 'bottom',
        'dropdowns': 'right',
        'buttons': 'left',
        'header_color': '#2d5a87',  # Lighter blue variant
        'search_button_position': 'separate'
    }
}

@app.get("/ui/positions/{student_id}", response_model=UIElementPosition)
async def get_ui_positions(student_id: int, db: Session = Depends(get_db)):
    """
    Get UI element positions assigned to a student for A/B testing.
    If student is not assigned, creates a new assignment.
    
    Args:
        student_id (int): The unique identifier of the student.
        db (Session): Database session.
    
    Returns:
        UIElementPosition: The UI element position configuration.
    """
    # Check if student exists
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if assignment exists
    assignment = db.query(ABTestAssignmentDB).filter(
        ABTestAssignmentDB.student_id == student_id
    ).first()
    
    if assignment:
        # Parse existing config
        ui_config = json.loads(assignment.ui_config) if assignment.ui_config else {}
        return {
            'student_id': assignment.student_id,
            'test_group': assignment.test_group,
            'ui_config': ui_config,
            'assigned_at': assignment.assigned_at.isoformat()
        }
    
    # Create new assignment (50/50 split based on student_id)
    test_group = 'A' if student_id % 2 == 0 else 'B'
    ui_config = UI_POSITION_VARIANTS[test_group]
    
    new_assignment = ABTestAssignmentDB(
        student_id=student_id,
        test_group=test_group,
        ui_config=json.dumps(ui_config)
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return {
        'student_id': new_assignment.student_id,
        'test_group': new_assignment.test_group,
        'ui_config': ui_config,
        'assigned_at': new_assignment.assigned_at.isoformat()
    }

@app.post("/ui/clicks", response_model=UIElementClick)
async def track_ui_click(click: UIElementClickCreate, db: Session = Depends(get_db)):
    """
    Track a click on a UI element for A/B testing analysis.
    
    Args:
        click (UIElementClickCreate): The click event data.
        db (Session): Database session.
    
    Returns:
        UIElementClick: The created click record.
    """
    # Check if student exists
    student = db.query(StudentDB).filter(StudentDB.student_id == click.student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get student's UI position assignment (REQUIRED - clicks must be tied to an assignment)
    assignment = db.query(ABTestAssignmentDB).filter(
        ABTestAssignmentDB.student_id == click.student_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=404, 
            detail="Student not assigned to A/B test group. Please assign student first."
        )
    
    # Auto-determine position from UI config (the assignment determines the position)
    element_position = click.element_position
    if not element_position:
        ui_config = json.loads(assignment.ui_config) if assignment.ui_config else {}
        if click.element_type == 'search_bar':
            element_position = ui_config.get('search_bar', 'top')
        elif click.element_type == 'dropdown':
            element_position = ui_config.get('dropdowns', 'left')
        elif click.element_type == 'button':
            element_position = ui_config.get('buttons', 'right')
    
    # Create click record - now connected to the assignment
    # Note: student_id is derived from assignment to ensure consistency
    click_record = UIElementClickDB(
        assignment_id=assignment.id,  # Primary relationship
        student_id=assignment.student_id,  # Derived from assignment (ensures consistency)
        element_type=click.element_type,
        element_id=click.element_id,
        element_position=element_position,
        click_count=1,
        page_url=click.page_url
    )
    db.add(click_record)
    db.commit()
    db.refresh(click_record)
    
    return {
        'id': click_record.id,
        'assignment_id': click_record.assignment_id,
        'student_id': click_record.student_id,
        'element_type': click_record.element_type,
        'element_id': click_record.element_id,
        'element_position': click_record.element_position,
        'click_count': click_record.click_count,
        'page_url': click_record.page_url,
        'clicked_at': click_record.clicked_at.isoformat()
    }

@app.get("/ui/statistics")
async def get_ui_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about UI element clicks for A/B testing analysis.
    Now includes test group (A/B) analysis since clicks are connected to assignments.
    
    Args:
        db (Session): Database session.
    
    Returns:
        dict: Statistics about clicks grouped by element type, position, and test group.
    """
    from sqlalchemy import func
    
    # Get all clicks with their assignments (join to get test_group)
    clicks = db.query(UIElementClickDB, ABTestAssignmentDB).join(
        ABTestAssignmentDB, UIElementClickDB.assignment_id == ABTestAssignmentDB.id
    ).all()
    
    # Group by element_type, element_position, and test_group
    stats = {}
    for click, assignment in clicks:
        # Create key with test group for better analysis
        key = f"{click.element_type}_{click.element_position or 'unknown'}_{assignment.test_group}"
        if key not in stats:
            stats[key] = {
                'element_type': click.element_type,
                'element_position': click.element_position or 'unknown',
                'test_group': assignment.test_group,
                'total_clicks': 0,
                'unique_users': set()
            }
        stats[key]['total_clicks'] += click.click_count
        stats[key]['unique_users'].add(click.student_id)
    
    # Convert sets to counts
    result = []
    for key, data in stats.items():
        result.append({
            'element_type': data['element_type'],
            'element_position': data['element_position'],
            'test_group': data['test_group'],
            'total_clicks': data['total_clicks'],
            'unique_users': len(data['unique_users'])
        })
    
    # Also get summary by test group
    group_a_clicks = sum(c.click_count for c, a in clicks if a.test_group == 'A')
    group_b_clicks = sum(c.click_count for c, a in clicks if a.test_group == 'B')
    
    return {
        'total_clicks': sum(c.click_count for c, _ in clicks),
        'total_records': len(clicks),
        'by_test_group': {
            'group_a': group_a_clicks,
            'group_b': group_b_clicks
        },
        'by_element': result
    }
