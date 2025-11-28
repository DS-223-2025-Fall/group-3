"""
FastAPI application for University Course Management System.
Provides REST API endpoints for managing students, courses, sections, and UI A/B testing.

This module defines all API endpoints including student CRUD operations and UI element
tracking for A/B testing purposes.
"""

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
    RecommendationResult, RecommendationResultCreate,
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
    Initialize database on startup. Creates tables and loads data if database is empty.
    
    Input:
        None
    
    Return:
        None
    """
    ensure_database_initialized()

# STUDENT ENDPOINTS

# GET Request - Retrieve a student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a student by their unique ID.

    Input:
        student_id (int): The unique identifier of the student.
        db (Session): Database session provided by dependency injection.

    Return:
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
    Create a new student record in the database.

    Input:
        student (StudentCreate): The student data to create.
        db (Session): Database session provided by dependency injection.

    Return:
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
    Update an existing student's details in the database.

    Input:
        student_id (int): The unique identifier of the student to update.
        updated_student (StudentCreate): The new student data.
        db (Session): Database session provided by dependency injection.

    Return:
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
    Delete a student by their unique ID from the database.

    Input:
        student_id (int): The unique identifier of the student to delete.
        db (Session): Database session provided by dependency injection.

    Return:
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

# SECTION ENDPOINTS

@app.get("/sections")
async def get_sections(
    year: Optional[int] = None,
    semester: Optional[str] = None,
    course_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all sections with optional filtering by year, semester, course type, and search text.
    Returns sections with joined data from courses, instructors, time slots, and locations for frontend display.
    
    Input:
        year (Optional[int]): Filter by year.
        semester (Optional[str]): Filter by semester (e.g., 'Fall', 'Spring', 'Summer').
        course_type (Optional[str]): Filter by course type (not currently used in model).
        search (Optional[str]): Search by course name.
        db (Session): Database session.
    
    Return:
        list[dict]: List of sections with joined course, instructor, time slot, and location data.
    """
    # Start with sections and join related tables
    query = db.query(
        SectionDB, CourseDB, InstructorDB, TimeSlotDB, LocationDB
    ).join(
        CourseDB, SectionDB.course_id == CourseDB.id
    ).join(
        InstructorDB, SectionDB.instructor_id == InstructorDB.id, isouter=True
    ).join(
        TimeSlotDB, SectionDB.time_slot_id == TimeSlotDB.time_slot_id, isouter=True
    ).join(
        LocationDB, SectionDB.roomID == LocationDB.room_id, isouter=True
    )
    
    # Filter by year and semester
    if year is not None:
        query = query.filter(TimeSlotDB.year == year)
    if semester:
        query = query.filter(TimeSlotDB.semester == semester)
    
    # Filter by course name if search provided
    if search:
        query = query.filter(CourseDB.name.ilike(f"%{search}%"))
    
    results = query.all()
    
    # Format response for frontend
    formatted_sections = []
    for section, course, instructor, timeslot, location in results:
        # Get clusters for this course
        clusters = db.query(CourseClusterDB.cluster_id).filter(
            CourseClusterDB.course_id == course.id
        ).all()
        cluster_ids = [c[0] for c in clusters]
        
        # Get enrollment count (taken seats)
        taken_seats = db.query(TakesDB).filter(
            TakesDB.section_id == section.id,
            TakesDB.status.in_(['enrolled', 'completed'])
        ).count()
        
        # Format time slot
        days = timeslot.day_of_week if timeslot else ""
        time = f"{timeslot.start_time}-{timeslot.end_time}" if timeslot and timeslot.start_time and timeslot.end_time else ""
        
        # Extract course code from name (first word) or use course ID as fallback
        course_code = str(course.id)
        if course.name and course.name.strip():
            name_parts = course.name.split()
            if name_parts:
                course_code = name_parts[0]
        
        formatted_sections.append({
            "id": str(section.id),
            "code": course_code,
            "name": course.name or "",
            "cluster": cluster_ids,
            "section": str(section.id),
            "instructor": instructor.name if instructor else "",
            "days": days,
            "time": time,
            "takenSeats": taken_seats,
            "totalSeats": section.capacity or 0,
            "location": location.building_room_name if location else "",
            "duration": section.duration or "",
            "syllabusUrl": section.syllabus_url
        })
    
    return formatted_sections

@app.get("/sections/{section_id}", response_model=Section)
async def get_section(section_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a section by its unique ID.
    
    Input:
        section_id (int): The unique identifier of the section.
        db (Session): Database session.
    
    Return:
        Section: The section's details.
    
    Raises:
        HTTPException: If the section is not found, raises a 404 error.
    """
    section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@app.post("/sections/", response_model=Section)
async def create_section(section: SectionCreate, db: Session = Depends(get_db)):
    """
    Create a new section record in the database.
    
    Input:
        section (SectionCreate): The section data to create.
        db (Session): Database session.
    
    Return:
        Section: The newly created section's details.
    """
    db_section = SectionDB(**section.model_dump())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@app.put("/sections/{section_id}", response_model=Section)
async def update_section(section_id: int, updated_section: SectionCreate, db: Session = Depends(get_db)):
    """
    Update an existing section's details in the database.
    
    Input:
        section_id (int): The unique identifier of the section to update.
        updated_section (SectionCreate): The new section data.
        db (Session): Database session.
    
    Return:
        Section: The updated section's details.
    
    Raises:
        HTTPException: If the section is not found, raises a 404 error.
    """
    section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    for key, value in updated_section.model_dump().items():
        setattr(section, key, value)
    db.commit()
    db.refresh(section)
    return section

@app.delete("/sections/{section_id}")
async def delete_section(section_id: int, db: Session = Depends(get_db)):
    """
    Delete a section by its unique ID from the database.
    
    Input:
        section_id (int): The unique identifier of the section to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the section is not found, raises a 404 error.
    """
    section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    db.delete(section)
    db.commit()
    return {"message": "Section deleted successfully"}

# COURSE ENDPOINTS

@app.get("/courses", response_model=list[Course])
async def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all courses with pagination.
    
    Input:
        skip (int): Number of records to skip, default 0.
        limit (int): Maximum number of records to return, default 100.
        db (Session): Database session.
    
    Return:
        list[Course]: List of courses.
    """
    courses = db.query(CourseDB).offset(skip).limit(limit).all()
    return courses

@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a course by its unique ID.
    
    Input:
        course_id (int): The unique identifier of the course.
        db (Session): Database session.
    
    Return:
        Course: The course's details.
    
    Raises:
        HTTPException: If the course is not found, raises a 404 error.
    """
    course = db.query(CourseDB).filter(CourseDB.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/courses/", response_model=Course)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """
    Create a new course record in the database.
    
    Input:
        course (CourseCreate): The course data to create.
        db (Session): Database session.
    
    Return:
        Course: The newly created course's details.
    """
    db_course = CourseDB(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: int, updated_course: CourseCreate, db: Session = Depends(get_db)):
    """
    Update an existing course's details in the database.
    
    Input:
        course_id (int): The unique identifier of the course to update.
        updated_course (CourseCreate): The new course data.
        db (Session): Database session.
    
    Return:
        Course: The updated course's details.
    
    Raises:
        HTTPException: If the course is not found, raises a 404 error.
    """
    course = db.query(CourseDB).filter(CourseDB.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in updated_course.model_dump().items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course

@app.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Delete a course by its unique ID from the database.
    
    Input:
        course_id (int): The unique identifier of the course to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the course is not found, raises a 404 error.
    """
    course = db.query(CourseDB).filter(CourseDB.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}

# INSTRUCTOR ENDPOINTS

@app.get("/instructors", response_model=list[Instructor])
async def get_instructors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all instructors with pagination.
    
    Input:
        skip (int): Number of records to skip, default 0.
        limit (int): Maximum number of records to return, default 100.
        db (Session): Database session.
    
    Return:
        list[Instructor]: List of instructors.
    """
    instructors = db.query(InstructorDB).offset(skip).limit(limit).all()
    return instructors

@app.get("/instructors/{instructor_id}", response_model=Instructor)
async def get_instructor(instructor_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an instructor by their unique ID.
    
    Input:
        instructor_id (int): The unique identifier of the instructor.
        db (Session): Database session.
    
    Return:
        Instructor: The instructor's details.
    
    Raises:
        HTTPException: If the instructor is not found, raises a 404 error.
    """
    instructor = db.query(InstructorDB).filter(InstructorDB.id == instructor_id).first()
    if instructor is None:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return instructor

@app.post("/instructors/", response_model=Instructor)
async def create_instructor(instructor: InstructorCreate, db: Session = Depends(get_db)):
    """
    Create a new instructor record in the database.
    
    Input:
        instructor (InstructorCreate): The instructor data to create.
        db (Session): Database session.
    
    Return:
        Instructor: The newly created instructor's details.
    """
    db_instructor = InstructorDB(**instructor.model_dump())
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    return db_instructor

@app.put("/instructors/{instructor_id}", response_model=Instructor)
async def update_instructor(instructor_id: int, updated_instructor: InstructorCreate, db: Session = Depends(get_db)):
    """
    Update an existing instructor's details in the database.
    
    Input:
        instructor_id (int): The unique identifier of the instructor to update.
        updated_instructor (InstructorCreate): The new instructor data.
        db (Session): Database session.
    
    Return:
        Instructor: The updated instructor's details.
    
    Raises:
        HTTPException: If the instructor is not found, raises a 404 error.
    """
    instructor = db.query(InstructorDB).filter(InstructorDB.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    for key, value in updated_instructor.model_dump().items():
        setattr(instructor, key, value)
    db.commit()
    db.refresh(instructor)
    return instructor

@app.delete("/instructors/{instructor_id}")
async def delete_instructor(instructor_id: int, db: Session = Depends(get_db)):
    """
    Delete an instructor by their unique ID from the database.
    
    Input:
        instructor_id (int): The unique identifier of the instructor to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the instructor is not found, raises a 404 error.
    """
    instructor = db.query(InstructorDB).filter(InstructorDB.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    db.delete(instructor)
    db.commit()
    return {"message": "Instructor deleted successfully"}

# DEPARTMENT ENDPOINTS

@app.get("/departments", response_model=list[Department])
async def get_departments(db: Session = Depends(get_db)):
    """
    Get all departments.
    
    Input:
        db (Session): Database session.
    
    Return:
        list[Department]: List of departments.
    """
    departments = db.query(DepartmentDB).all()
    return departments

@app.get("/departments/{dept_name}", response_model=Department)
async def get_department(dept_name: str, db: Session = Depends(get_db)):
    """
    Retrieve a department by its name.
    
    Input:
        dept_name (str): The name of the department.
        db (Session): Database session.
    
    Return:
        Department: The department's details.
    
    Raises:
        HTTPException: If the department is not found, raises a 404 error.
    """
    department = db.query(DepartmentDB).filter(DepartmentDB.dept_name == dept_name).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@app.post("/departments/", response_model=Department)
async def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Create a new department record in the database.
    
    Input:
        department (DepartmentCreate): The department data to create.
        db (Session): Database session.
    
    Return:
        Department: The newly created department's details.
    """
    db_department = DepartmentDB(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@app.put("/departments/{dept_name}", response_model=Department)
async def update_department(dept_name: str, updated_department: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Update an existing department's details in the database.
    
    Input:
        dept_name (str): The name of the department to update.
        updated_department (DepartmentCreate): The new department data.
        db (Session): Database session.
    
    Return:
        Department: The updated department's details.
    
    Raises:
        HTTPException: If the department is not found, raises a 404 error.
    """
    department = db.query(DepartmentDB).filter(DepartmentDB.dept_name == dept_name).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    for key, value in updated_department.model_dump().items():
        setattr(department, key, value)
    db.commit()
    db.refresh(department)
    return department

@app.delete("/departments/{dept_name}")
async def delete_department(dept_name: str, db: Session = Depends(get_db)):
    """
    Delete a department by its name from the database.
    
    Input:
        dept_name (str): The name of the department to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the department is not found, raises a 404 error.
    """
    department = db.query(DepartmentDB).filter(DepartmentDB.dept_name == dept_name).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(department)
    db.commit()
    return {"message": "Department deleted successfully"}

# PROGRAM ENDPOINTS

@app.get("/programs", response_model=list[Program])
async def get_programs(db: Session = Depends(get_db)):
    """
    Get all programs.
    
    Input:
        db (Session): Database session.
    
    Return:
        list[Program]: List of programs.
    """
    programs = db.query(ProgramDB).all()
    return programs

@app.get("/programs/{prog_name}", response_model=Program)
async def get_program(prog_name: str, db: Session = Depends(get_db)):
    """
    Retrieve a program by its name.
    
    Input:
        prog_name (str): The name of the program.
        db (Session): Database session.
    
    Return:
        Program: The program's details.
    
    Raises:
        HTTPException: If the program is not found, raises a 404 error.
    """
    program = db.query(ProgramDB).filter(ProgramDB.prog_name == prog_name).first()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return program

@app.post("/programs/", response_model=Program)
async def create_program(program: ProgramCreate, db: Session = Depends(get_db)):
    """
    Create a new program record in the database.
    
    Input:
        program (ProgramCreate): The program data to create.
        db (Session): Database session.
    
    Return:
        Program: The newly created program's details.
    """
    db_program = ProgramDB(**program.model_dump())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

@app.put("/programs/{prog_name}", response_model=Program)
async def update_program(prog_name: str, updated_program: ProgramCreate, db: Session = Depends(get_db)):
    """
    Update an existing program's details in the database.
    
    Input:
        prog_name (str): The name of the program to update.
        updated_program (ProgramCreate): The new program data.
        db (Session): Database session.
    
    Return:
        Program: The updated program's details.
    
    Raises:
        HTTPException: If the program is not found, raises a 404 error.
    """
    program = db.query(ProgramDB).filter(ProgramDB.prog_name == prog_name).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    for key, value in updated_program.model_dump().items():
        setattr(program, key, value)
    db.commit()
    db.refresh(program)
    return program

@app.delete("/programs/{prog_name}")
async def delete_program(prog_name: str, db: Session = Depends(get_db)):
    """
    Delete a program by its name from the database.
    
    Input:
        prog_name (str): The name of the program to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the program is not found, raises a 404 error.
    """
    program = db.query(ProgramDB).filter(ProgramDB.prog_name == prog_name).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    db.delete(program)
    db.commit()
    return {"message": "Program deleted successfully"}

# LOCATION ENDPOINTS

@app.get("/locations", response_model=list[Location])
async def get_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all locations with pagination.
    
    Input:
        skip (int): Number of records to skip, default 0.
        limit (int): Maximum number of records to return, default 100.
        db (Session): Database session.
    
    Return:
        list[Location]: List of locations.
    """
    locations = db.query(LocationDB).offset(skip).limit(limit).all()
    return locations

@app.get("/locations/{room_id}", response_model=Location)
async def get_location(room_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a location by its room ID.
    
    Input:
        room_id (int): The unique identifier of the location.
        db (Session): Database session.
    
    Return:
        Location: The location's details.
    
    Raises:
        HTTPException: If the location is not found, raises a 404 error.
    """
    location = db.query(LocationDB).filter(LocationDB.room_id == room_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@app.post("/locations/", response_model=Location)
async def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """
    Create a new location record in the database.
    
    Input:
        location (LocationCreate): The location data to create.
        db (Session): Database session.
    
    Return:
        Location: The newly created location's details.
    """
    db_location = LocationDB(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.put("/locations/{room_id}", response_model=Location)
async def update_location(room_id: int, updated_location: LocationCreate, db: Session = Depends(get_db)):
    """
    Update an existing location's details in the database.
    
    Input:
        room_id (int): The unique identifier of the location to update.
        updated_location (LocationCreate): The new location data.
        db (Session): Database session.
    
    Return:
        Location: The updated location's details.
    
    Raises:
        HTTPException: If the location is not found, raises a 404 error.
    """
    location = db.query(LocationDB).filter(LocationDB.room_id == room_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in updated_location.model_dump().items():
        setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location

@app.delete("/locations/{room_id}")
async def delete_location(room_id: int, db: Session = Depends(get_db)):
    """
    Delete a location by its room ID from the database.
    
    Input:
        room_id (int): The unique identifier of the location to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the location is not found, raises a 404 error.
    """
    location = db.query(LocationDB).filter(LocationDB.room_id == room_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(location)
    db.commit()
    return {"message": "Location deleted successfully"}

# TIMESLOT ENDPOINTS

@app.get("/timeslots", response_model=list[TimeSlot])
async def get_timeslots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all time slots with pagination.
    
    Input:
        skip (int): Number of records to skip, default 0.
        limit (int): Maximum number of records to return, default 100.
        db (Session): Database session.
    
    Return:
        list[TimeSlot]: List of time slots.
    """
    timeslots = db.query(TimeSlotDB).offset(skip).limit(limit).all()
    return timeslots

@app.get("/timeslots/{time_slot_id}", response_model=TimeSlot)
async def get_timeslot(time_slot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a time slot by its unique ID.
    
    Input:
        time_slot_id (int): The unique identifier of the time slot.
        db (Session): Database session.
    
    Return:
        TimeSlot: The time slot's details.
    
    Raises:
        HTTPException: If the time slot is not found, raises a 404 error.
    """
    timeslot = db.query(TimeSlotDB).filter(TimeSlotDB.time_slot_id == time_slot_id).first()
    if timeslot is None:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return timeslot

@app.post("/timeslots/", response_model=TimeSlot)
async def create_timeslot(timeslot: TimeSlotCreate, db: Session = Depends(get_db)):
    """
    Create a new time slot record in the database.
    
    Input:
        timeslot (TimeSlotCreate): The time slot data to create.
        db (Session): Database session.
    
    Return:
        TimeSlot: The newly created time slot's details.
    """
    db_timeslot = TimeSlotDB(**timeslot.model_dump())
    db.add(db_timeslot)
    db.commit()
    db.refresh(db_timeslot)
    return db_timeslot

@app.put("/timeslots/{time_slot_id}", response_model=TimeSlot)
async def update_timeslot(time_slot_id: int, updated_timeslot: TimeSlotCreate, db: Session = Depends(get_db)):
    """
    Update an existing time slot's details in the database.
    
    Input:
        time_slot_id (int): The unique identifier of the time slot to update.
        updated_timeslot (TimeSlotCreate): The new time slot data.
        db (Session): Database session.
    
    Return:
        TimeSlot: The updated time slot's details.
    
    Raises:
        HTTPException: If the time slot is not found, raises a 404 error.
    """
    timeslot = db.query(TimeSlotDB).filter(TimeSlotDB.time_slot_id == time_slot_id).first()
    if not timeslot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    for key, value in updated_timeslot.model_dump().items():
        setattr(timeslot, key, value)
    db.commit()
    db.refresh(timeslot)
    return timeslot

@app.delete("/timeslots/{time_slot_id}")
async def delete_timeslot(time_slot_id: int, db: Session = Depends(get_db)):
    """
    Delete a time slot by its unique ID from the database.
    
    Input:
        time_slot_id (int): The unique identifier of the time slot to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the time slot is not found, raises a 404 error.
    """
    timeslot = db.query(TimeSlotDB).filter(TimeSlotDB.time_slot_id == time_slot_id).first()
    if not timeslot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    db.delete(timeslot)
    db.commit()
    return {"message": "Time slot deleted successfully"}

# TAKES ENDPOINTS (Student Enrollments)

@app.get("/takes", response_model=list[Takes])
async def get_takes(student_id: Optional[int] = None, section_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get all student enrollments (takes) with optional filtering.
    
    Input:
        student_id (Optional[int]): Filter by student ID.
        section_id (Optional[int]): Filter by section ID.
        db (Session): Database session.
    
    Return:
        list[Takes]: List of enrollment records.
    """
    query = db.query(TakesDB)
    if student_id:
        query = query.filter(TakesDB.student_id == student_id)
    if section_id:
        query = query.filter(TakesDB.section_id == section_id)
    takes = query.all()
    return takes

@app.post("/takes/", response_model=Takes)
async def create_takes(takes: TakesCreate, db: Session = Depends(get_db)):
    """
    Create a new student enrollment record in the database.
    
    Input:
        takes (TakesCreate): The enrollment data to create.
        db (Session): Database session.
    
    Return:
        Takes: The newly created enrollment record.
    """
    db_takes = TakesDB(**takes.model_dump())
    db.add(db_takes)
    db.commit()
    db.refresh(db_takes)
    return db_takes

@app.delete("/takes/")
async def delete_takes(student_id: int, section_id: int, db: Session = Depends(get_db)):
    """
    Delete a student enrollment record from the database.
    
    Input:
        student_id (int): The unique identifier of the student.
        section_id (int): The unique identifier of the section.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the enrollment is not found, raises a 404 error.
    """
    takes = db.query(TakesDB).filter(
        TakesDB.student_id == student_id,
        TakesDB.section_id == section_id
    ).first()
    if not takes:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(takes)
    db.commit()
    return {"message": "Enrollment deleted successfully"}

# PREREQUISITES ENDPOINTS

@app.get("/prerequisites", response_model=list[Prerequisites])
async def get_prerequisites(course_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get all prerequisites with optional filtering by course ID.
    
    Input:
        course_id (Optional[int]): Filter by course ID.
        db (Session): Database session.
    
    Return:
        list[Prerequisites]: List of prerequisite records.
    """
    query = db.query(PrerequisitesDB)
    if course_id:
        query = query.filter(PrerequisitesDB.course_id == course_id)
    prerequisites = query.all()
    return prerequisites

@app.post("/prerequisites/", response_model=Prerequisites)
async def create_prerequisites(prerequisites: PrerequisitesCreate, db: Session = Depends(get_db)):
    """
    Create a new prerequisite record in the database.
    
    Input:
        prerequisites (PrerequisitesCreate): The prerequisite data to create.
        db (Session): Database session.
    
    Return:
        Prerequisites: The newly created prerequisite record.
    """
    db_prerequisites = PrerequisitesDB(**prerequisites.model_dump())
    db.add(db_prerequisites)
    db.commit()
    db.refresh(db_prerequisites)
    return db_prerequisites

@app.delete("/prerequisites/")
async def delete_prerequisites(course_id: int, prerequisite_id: int, db: Session = Depends(get_db)):
    """
    Delete a prerequisite record from the database.
    
    Input:
        course_id (int): The unique identifier of the course.
        prerequisite_id (int): The unique identifier of the prerequisite course.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the prerequisite is not found, raises a 404 error.
    """
    prerequisites = db.query(PrerequisitesDB).filter(
        PrerequisitesDB.course_id == course_id,
        PrerequisitesDB.prerequisite_id == prerequisite_id
    ).first()
    if not prerequisites:
        raise HTTPException(status_code=404, detail="Prerequisite not found")
    db.delete(prerequisites)
    db.commit()
    return {"message": "Prerequisite deleted successfully"}

# WORKS ENDPOINTS (Instructor-Department relationship)

@app.get("/works", response_model=list[Works])
async def get_works(instructorid: Optional[int] = None, dept_name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all instructor-department relationships with optional filtering.
    
    Input:
        instructorid (Optional[int]): Filter by instructor ID.
        dept_name (Optional[str]): Filter by department name.
        db (Session): Database session.
    
    Return:
        list[Works]: List of instructor-department relationships.
    """
    query = db.query(WorksDB)
    if instructorid:
        query = query.filter(WorksDB.instructorid == instructorid)
    if dept_name:
        query = query.filter(WorksDB.dept_name == dept_name)
    works = query.all()
    return works

@app.post("/works/", response_model=Works)
async def create_works(works: WorksCreate, db: Session = Depends(get_db)):
    """
    Create a new instructor-department relationship record in the database.
    
    Input:
        works (WorksCreate): The relationship data to create.
        db (Session): Database session.
    
    Return:
        Works: The newly created relationship record.
    """
    db_works = WorksDB(**works.model_dump())
    db.add(db_works)
    db.commit()
    db.refresh(db_works)
    return db_works

@app.delete("/works/")
async def delete_works(instructorid: int, dept_name: str, db: Session = Depends(get_db)):
    """
    Delete an instructor-department relationship record from the database.
    
    Input:
        instructorid (int): The unique identifier of the instructor.
        dept_name (str): The name of the department.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the relationship is not found, raises a 404 error.
    """
    works = db.query(WorksDB).filter(
        WorksDB.instructorid == instructorid,
        WorksDB.dept_name == dept_name
    ).first()
    if not works:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(works)
    db.commit()
    return {"message": "Relationship deleted successfully"}

# HASCOURSE ENDPOINTS (Program-Course relationship)

@app.get("/hascourse", response_model=list[HasCourse])
async def get_hascourse(prog_name: Optional[str] = None, courseid: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get all program-course relationships with optional filtering.
    
    Input:
        prog_name (Optional[str]): Filter by program name.
        courseid (Optional[int]): Filter by course ID.
        db (Session): Database session.
    
    Return:
        list[HasCourse]: List of program-course relationships.
    """
    query = db.query(HasCourseDB)
    if prog_name:
        query = query.filter(HasCourseDB.prog_name == prog_name)
    if courseid:
        query = query.filter(HasCourseDB.courseid == courseid)
    hascourse = query.all()
    return hascourse

@app.post("/hascourse/", response_model=HasCourse)
async def create_hascourse(hascourse: HasCourseCreate, db: Session = Depends(get_db)):
    """
    Create a new program-course relationship record in the database.
    
    Input:
        hascourse (HasCourseCreate): The relationship data to create.
        db (Session): Database session.
    
    Return:
        HasCourse: The newly created relationship record.
    """
    db_hascourse = HasCourseDB(**hascourse.model_dump())
    db.add(db_hascourse)
    db.commit()
    db.refresh(db_hascourse)
    return db_hascourse

@app.delete("/hascourse/")
async def delete_hascourse(prog_name: str, courseid: int, db: Session = Depends(get_db)):
    """
    Delete a program-course relationship record from the database.
    
    Input:
        prog_name (str): The name of the program.
        courseid (int): The unique identifier of the course.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the relationship is not found, raises a 404 error.
    """
    hascourse = db.query(HasCourseDB).filter(
        HasCourseDB.prog_name == prog_name,
        HasCourseDB.courseid == courseid
    ).first()
    if not hascourse:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(hascourse)
    db.commit()
    return {"message": "Relationship deleted successfully"}

# CLUSTER ENDPOINTS

@app.get("/clusters", response_model=list[Cluster])
async def get_clusters(prog_name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all clusters with optional filtering by program name.
    
    Input:
        prog_name (Optional[str]): Filter by program name.
        db (Session): Database session.
    
    Return:
        list[Cluster]: List of clusters.
    """
    query = db.query(ClusterDB)
    if prog_name:
        query = query.filter(ClusterDB.prog_name == prog_name)
    clusters = query.all()
    return clusters

@app.get("/clusters/{cluster_id}", response_model=Cluster)
async def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a cluster by its unique ID.
    
    Input:
        cluster_id (int): The unique identifier of the cluster.
        db (Session): Database session.
    
    Return:
        Cluster: The cluster's details.
    
    Raises:
        HTTPException: If the cluster is not found, raises a 404 error.
    """
    cluster = db.query(ClusterDB).filter(ClusterDB.cluster_id == cluster_id).first()
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@app.post("/clusters/", response_model=Cluster)
async def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_db)):
    """
    Create a new cluster record in the database.
    
    Input:
        cluster (ClusterCreate): The cluster data to create.
        db (Session): Database session.
    
    Return:
        Cluster: The newly created cluster's details.
    """
    db_cluster = ClusterDB(**cluster.model_dump())
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster

@app.put("/clusters/{cluster_id}", response_model=Cluster)
async def update_cluster(cluster_id: int, updated_cluster: ClusterCreate, db: Session = Depends(get_db)):
    """
    Update an existing cluster's details in the database.
    
    Input:
        cluster_id (int): The unique identifier of the cluster to update.
        updated_cluster (ClusterCreate): The new cluster data.
        db (Session): Database session.
    
    Return:
        Cluster: The updated cluster's details.
    
    Raises:
        HTTPException: If the cluster is not found, raises a 404 error.
    """
    cluster = db.query(ClusterDB).filter(ClusterDB.cluster_id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    for key, value in updated_cluster.model_dump().items():
        setattr(cluster, key, value)
    db.commit()
    db.refresh(cluster)
    return cluster

@app.delete("/clusters/{cluster_id}")
async def delete_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """
    Delete a cluster by its unique ID from the database.
    
    Input:
        cluster_id (int): The unique identifier of the cluster to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the cluster is not found, raises a 404 error.
    """
    cluster = db.query(ClusterDB).filter(ClusterDB.cluster_id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db.delete(cluster)
    db.commit()
    return {"message": "Cluster deleted successfully"}

# COURSECLUSTER ENDPOINTS (Course-Cluster relationship)

@app.get("/coursecluster", response_model=list[CourseCluster])
async def get_coursecluster(course_id: Optional[int] = None, cluster_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get all course-cluster relationships with optional filtering.
    
    Input:
        course_id (Optional[int]): Filter by course ID.
        cluster_id (Optional[int]): Filter by cluster ID.
        db (Session): Database session.
    
    Return:
        list[CourseCluster]: List of course-cluster relationships.
    """
    query = db.query(CourseClusterDB)
    if course_id:
        query = query.filter(CourseClusterDB.course_id == course_id)
    if cluster_id:
        query = query.filter(CourseClusterDB.cluster_id == cluster_id)
    courseclusters = query.all()
    return courseclusters

@app.post("/coursecluster/", response_model=CourseCluster)
async def create_coursecluster(coursecluster: CourseClusterCreate, db: Session = Depends(get_db)):
    """
    Create a new course-cluster relationship record in the database.
    
    Input:
        coursecluster (CourseClusterCreate): The relationship data to create.
        db (Session): Database session.
    
    Return:
        CourseCluster: The newly created relationship record.
    """
    db_coursecluster = CourseClusterDB(**coursecluster.model_dump())
    db.add(db_coursecluster)
    db.commit()
    db.refresh(db_coursecluster)
    return db_coursecluster

@app.delete("/coursecluster/")
async def delete_coursecluster(course_id: int, cluster_id: int, db: Session = Depends(get_db)):
    """
    Delete a course-cluster relationship record from the database.
    
    Input:
        course_id (int): The unique identifier of the course.
        cluster_id (int): The unique identifier of the cluster.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the relationship is not found, raises a 404 error.
    """
    coursecluster = db.query(CourseClusterDB).filter(
        CourseClusterDB.course_id == course_id,
        CourseClusterDB.cluster_id == cluster_id
    ).first()
    if not coursecluster:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(coursecluster)
    db.commit()
    return {"message": "Relationship deleted successfully"}

# PREFERRED ENDPOINTS (Student-Course preferences)

@app.get("/preferred", response_model=list[Preferred])
async def get_preferred(student_id: Optional[int] = None, course_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get all student-course preferences with optional filtering.
    
    Input:
        student_id (Optional[int]): Filter by student ID.
        course_id (Optional[int]): Filter by course ID.
        db (Session): Database session.
    
    Return:
        list[Preferred]: List of student-course preferences.
    """
    query = db.query(PreferredDB)
    if student_id:
        query = query.filter(PreferredDB.student_id == student_id)
    if course_id:
        query = query.filter(PreferredDB.course_id == course_id)
    preferred = query.all()
    return preferred

@app.post("/preferred/", response_model=Preferred)
async def create_preferred(preferred: PreferredCreate, db: Session = Depends(get_db)):
    """
    Create a new student-course preference record in the database.
    
    Input:
        preferred (PreferredCreate): The preference data to create.
        db (Session): Database session.
    
    Return:
        Preferred: The newly created preference record.
    """
    db_preferred = PreferredDB(**preferred.model_dump())
    db.add(db_preferred)
    db.commit()
    db.refresh(db_preferred)
    return db_preferred

@app.delete("/preferred/")
async def delete_preferred(student_id: int, course_id: int, db: Session = Depends(get_db)):
    """
    Delete a student-course preference record from the database.
    
    Input:
        student_id (int): The unique identifier of the student.
        course_id (int): The unique identifier of the course.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the preference is not found, raises a 404 error.
    """
    preferred = db.query(PreferredDB).filter(
        PreferredDB.student_id == student_id,
        PreferredDB.course_id == course_id
    ).first()
    if not preferred:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(preferred)
    db.commit()
    return {"message": "Preference deleted successfully"}

# RECOMMENDATION RESULT ENDPOINTS

@app.get("/recommendation-results", response_model=list[RecommendationResult])
async def get_recommendation_results(
    student_id: Optional[int] = None,
    semester: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all recommendation results with optional filtering by student, semester, and year.
    
    Input:
        student_id (Optional[int]): Filter by student ID.
        semester (Optional[str]): Filter by semester (e.g., 'Fall', 'Spring', 'Summer').
        year (Optional[int]): Filter by year.
        db (Session): Database session.
    
    Return:
        list[RecommendationResult]: List of recommendation results.
    """
    query = db.query(RecommendationResultDB)
    if student_id:
        query = query.filter(RecommendationResultDB.student_id == student_id)
    if semester:
        query = query.filter(RecommendationResultDB.semester == semester)
    if year:
        query = query.filter(RecommendationResultDB.year == year)
    results = query.order_by(RecommendationResultDB.created_at.desc()).all()
    
    # Format response with ISO timestamps
    formatted_results = []
    for result in results:
        result_dict = {
            "id": result.id,
            "student_id": result.student_id,
            "course_id": result.course_id,
            "recommended_section_id": result.recommended_section_id,
            "course_name": result.course_name,
            "cluster": result.cluster,
            "credits": result.credits,
            "time_slot": result.time_slot,
            "recommendation_score": result.recommendation_score,
            "why_recommended": result.why_recommended,
            "slot_number": result.slot_number,
            "model_version": result.model_version,
            "time_preference": result.time_preference,
            "semester": result.semester,
            "year": result.year,
            "created_at": result.created_at.isoformat() if result.created_at else "",
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        }
        formatted_results.append(result_dict)
    return formatted_results

@app.get("/recommendation-results/{result_id}", response_model=RecommendationResult)
async def get_recommendation_result(result_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a recommendation result by its unique ID.
    
    Input:
        result_id (int): The unique identifier of the recommendation result.
        db (Session): Database session.
    
    Return:
        RecommendationResult: The recommendation result's details.
    
    Raises:
        HTTPException: If the recommendation result is not found, raises a 404 error.
    """
    result = db.query(RecommendationResultDB).filter(RecommendationResultDB.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Recommendation result not found")
    
    return {
        "id": result.id,
        "student_id": result.student_id,
        "course_id": result.course_id,
        "recommended_section_id": result.recommended_section_id,
        "course_name": result.course_name,
        "cluster": result.cluster,
        "credits": result.credits,
        "time_slot": result.time_slot,
        "recommendation_score": result.recommendation_score,
        "why_recommended": result.why_recommended,
        "slot_number": result.slot_number,
        "model_version": result.model_version,
        "time_preference": result.time_preference,
        "semester": result.semester,
        "year": result.year,
        "created_at": result.created_at.isoformat() if result.created_at else "",
        "updated_at": result.updated_at.isoformat() if result.updated_at else None
    }

@app.post("/recommendation-results/", response_model=RecommendationResult)
async def create_recommendation_result(
    recommendation: RecommendationResultCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new recommendation result record in the database.
    
    Input:
        recommendation (RecommendationResultCreate): The recommendation result data to create.
        db (Session): Database session.
    
    Return:
        RecommendationResult: The newly created recommendation result's details.
    """
    db_recommendation = RecommendationResultDB(**recommendation.model_dump())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    
    return {
        "id": db_recommendation.id,
        "student_id": db_recommendation.student_id,
        "course_id": db_recommendation.course_id,
        "recommended_section_id": db_recommendation.recommended_section_id,
        "course_name": db_recommendation.course_name,
        "cluster": db_recommendation.cluster,
        "credits": db_recommendation.credits,
        "time_slot": db_recommendation.time_slot,
        "recommendation_score": db_recommendation.recommendation_score,
        "why_recommended": db_recommendation.why_recommended,
        "slot_number": db_recommendation.slot_number,
        "model_version": db_recommendation.model_version,
        "time_preference": db_recommendation.time_preference,
        "semester": db_recommendation.semester,
        "year": db_recommendation.year,
        "created_at": db_recommendation.created_at.isoformat() if db_recommendation.created_at else "",
        "updated_at": db_recommendation.updated_at.isoformat() if db_recommendation.updated_at else None
    }

@app.put("/recommendation-results/{result_id}", response_model=RecommendationResult)
async def update_recommendation_result(
    result_id: int,
    updated_recommendation: RecommendationResultCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing recommendation result's details in the database.
    
    Input:
        result_id (int): The unique identifier of the recommendation result to update.
        updated_recommendation (RecommendationResultCreate): The new recommendation result data.
        db (Session): Database session.
    
    Return:
        RecommendationResult: The updated recommendation result's details.
    
    Raises:
        HTTPException: If the recommendation result is not found, raises a 404 error.
    """
    result = db.query(RecommendationResultDB).filter(RecommendationResultDB.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation result not found")
    
    for key, value in updated_recommendation.model_dump().items():
        setattr(result, key, value)
    db.commit()
    db.refresh(result)
    
    return {
        "id": result.id,
        "student_id": result.student_id,
        "course_id": result.course_id,
        "recommended_section_id": result.recommended_section_id,
        "course_name": result.course_name,
        "cluster": result.cluster,
        "credits": result.credits,
        "time_slot": result.time_slot,
        "recommendation_score": result.recommendation_score,
        "why_recommended": result.why_recommended,
        "slot_number": result.slot_number,
        "model_version": result.model_version,
        "time_preference": result.time_preference,
        "semester": result.semester,
        "year": result.year,
        "created_at": result.created_at.isoformat() if result.created_at else "",
        "updated_at": result.updated_at.isoformat() if result.updated_at else None
    }

@app.delete("/recommendation-results/{result_id}")
async def delete_recommendation_result(result_id: int, db: Session = Depends(get_db)):
    """
    Delete a recommendation result by its unique ID from the database.
    
    Input:
        result_id (int): The unique identifier of the recommendation result to delete.
        db (Session): Database session.
    
    Return:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the recommendation result is not found, raises a 404 error.
    """
    result = db.query(RecommendationResultDB).filter(RecommendationResultDB.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation result not found")
    db.delete(result)
    db.commit()
    return {"message": "Recommendation result deleted successfully"}

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
    Get UI element positions assigned to a student for A/B testing. If student is not assigned, creates a new assignment.
    
    Input:
        student_id (int): The unique identifier of the student.
        db (Session): Database session.
    
    Return:
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
    
    Input:
        click (UIElementClickCreate): The click event data.
        db (Session): Database session.
    
    Return:
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
    Get statistics about UI element clicks for A/B testing analysis. Includes test group (A/B) analysis since clicks are connected to assignments.
    
    Input:
        db (Session): Database session.
    
    Return:
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
