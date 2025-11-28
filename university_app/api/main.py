# Import all models so they are registered with SQLAlchemy Base metadata
# This ensures all tables are created when Base.metadata.create_all() is called
from Database.models import (
    StudentDB, SectionDB, TakesDB, LocationDB, InstructorDB, 
    DepartmentDB, ProgramDB, CourseDB, TimeSlotDB, PrerequisitesDB, 
    WorksDB, HasCourseDB, ClusterDB, CourseClusterDB, PreferredDB, Base
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
    Preferred, PreferredCreate
)
from Database.database import get_db, engine
from Database.init_db import ensure_database_initialized

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="University Course Management API")

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
