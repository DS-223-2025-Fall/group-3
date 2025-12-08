"""
FastAPI application for University Course Management System.
Provides REST API endpoints for managing students, courses, and sections.

This module defines all API endpoints including student CRUD operations.
"""

from Database.models import (
    UserDB, StudentDB, SectionDB, SectionNameDB, TakesDB, LocationDB, InstructorDB, 
    DepartmentDB, ProgramDB, CourseDB, TimeSlotDB, PrerequisitesDB, 
    WorksDB, HasCourseDB, ClusterDB, CourseClusterDB, PreferredDB,
    RecommendationResultDB,
    DraftScheduleDB, DraftScheduleSectionDB
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
    DraftSchedule, DraftScheduleCreate, DraftScheduleUpdate
)
from Database.database import get_db, engine
from Database.init_db import ensure_database_initialized

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from datetime import date
from typing import Optional, List

if os.path.exists('/shared'):
    sys.path.insert(0, '/')
else:
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if os.path.exists(os.path.join(parent_dir, 'shared')):
        sys.path.insert(0, parent_dir)

try:
    from shared.recommender_helpers import generate_recommendations_for_student
    from shared.semester_scheduler import SemesterScheduler
except ImportError as e:
    # If import fails, the endpoint will show a clear error
    import traceback
    print(f"Warning: Could not import shared module: {e}")
    print(f"Python path: {sys.path}")
    traceback.print_exc()
    generate_recommendations_for_student = None
    SemesterScheduler = None

app = FastAPI(title="University Course Management API")

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",") if os.environ.get("ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYLLABI_DIR = "/api/syllabi"
if os.path.exists(SYLLABI_DIR):
    app.mount("/syllabi", StaticFiles(directory=SYLLABI_DIR), name="syllabi")


@app.on_event("startup")
async def startup_event():
    """
    Description:
        Initialize database on startup. Creates tables and loads data if database is empty.
    
    Input:
        None
    
    Output:
        None
    """
    ensure_database_initialized()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login", response_model=dict)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Description:
        Authenticate a user with username and password.
    
    Input:
        credentials (LoginRequest): Username and password
        db (Session): Database session
    
    Output:
        dict: User information including user_id, username, student_id, and student info
    
    Raises:
        HTTPException: If credentials are invalid
    """
    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    
    if not user or user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Get student information if linked
    student = None
    if user.student_id:
        student = db.query(StudentDB).filter(StudentDB.student_id == user.student_id).first()
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "student_id": user.student_id,
        "student": {
            "student_id": student.student_id,
            "student_name": student.student_name,
            "credit": student.credit,
            "program_name": student.program_name
        } if student else None
    }

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Description:
        Retrieve a student by their unique ID.

    Input:
        student_id (int): The unique identifier of the student.
        db (Session): Database session provided by dependency injection.

    Output:
        Student: The student's details.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/students/", response_model=Student)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student record in the database.

    Input:
        student (StudentCreate): The student data to create.
        db (Session): Database session provided by dependency injection.

    Output:
        Student: The newly created student's details.
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        db_student = StudentDB(
            student_name=student.student_name,
            credit=student.credit,
            program_name=student.program_name
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, updated_student: StudentCreate, db: Session = Depends(get_db)):
    """
    Update an existing student's details in the database.

    Input:
        student_id (int): The unique identifier of the student to update.
        updated_student (StudentCreate): The new student data.
        db (Session): Database session provided by dependency injection.

    Output:
        Student: The updated student's details.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    try:
        student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        for key, value in updated_student.model_dump().items():
            setattr(student, key, value)
        db.commit()
        db.refresh(student)
        return student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")


@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student by their unique ID from the database.

    Input:
        student_id (int): The unique identifier of the student to delete.
        db (Session): Database session provided by dependency injection.

    Output:
        dict: A message confirming successful deletion.

    Raises:
        HTTPException: If the student is not found, raises a 404 error.
    """
    try:
        student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        db.delete(student)
        db.commit()
        return {"message": "Student deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting student: {str(e)}")

# SECTION ENDPOINTS

@app.get("/sections")
async def get_sections(
    year: Optional[str] = None,
    semester: Optional[str] = None,
    course_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Description:
        Get all sections with optional filtering by year, semester, course type, and search text.
        Returns sections with joined data from courses, instructors, time slots, and locations for frontend display.
    
    Input:
        year (Optional[int]): Filter by year.
        semester (Optional[str]): Filter by semester (e.g., 'Fall', 'Spring', 'Summer').
        course_type (Optional[str]): Filter by course type (GenEd, Major, Elective).
        search (Optional[str]): Search by course name.
        db (Session): Database session.
    
    Output:
        list[dict]: List of sections with joined course, instructor, time slot, and location data.
    """
    # Filter by course type if provided - course_type is now the program name directly
    filtered_course_ids = None
    if course_type and course_type != "All":
        # Get course IDs that belong to this program
        course_id_list = db.query(HasCourseDB.courseid).filter(
            HasCourseDB.prog_name == course_type
        ).distinct().all()
        filtered_course_ids = [cid[0] for cid in course_id_list]
    
    # Start with sections and join related tables
    query = db.query(
        SectionDB, CourseDB, InstructorDB, TimeSlotDB, LocationDB, SectionNameDB
    ).join(
        CourseDB, SectionDB.course_id == CourseDB.id
    ).join(
        InstructorDB, SectionDB.instructor_id == InstructorDB.id, isouter=True
    ).join(
        TimeSlotDB, SectionDB.time_slot_id == TimeSlotDB.time_slot_id, isouter=True
    ).join(
        LocationDB, SectionDB.roomID == LocationDB.room_id, isouter=True
    ).join(
        SectionNameDB, SectionDB.id == SectionNameDB.section_id, isouter=True
    )
    
    # Apply course type filter if provided
    if filtered_course_ids is not None:
        query = query.filter(CourseDB.id.in_(filtered_course_ids))
    
    # Filter by year and semester
    if year is not None:
        try:
            year_int = int(year)
            query = query.filter(TimeSlotDB.year == year_int)
        except (ValueError, TypeError):
            pass  # Invalid year format, skip filter
    if semester:
        query = query.filter(TimeSlotDB.semester == semester)
    
    # Filter by course name if search provided
    if search:
        query = query.filter(CourseDB.name.ilike(f"%{search}%"))
    
    results = query.all()
    
    # Helper function to expand MWF/TTh days
    def expand_days(day_str):
        """Expand single day to MWF or TTh group if applicable"""
        if not day_str:
            return day_str
        
        day_lower = day_str.strip().lower()
        # MWF pattern: if any of Mon, Wed, Fri, return all three
        if day_lower in ['mon', 'monday']:
            return "Monday, Wednesday, Friday"
        elif day_lower in ['wed', 'wednesday']:
            return "Monday, Wednesday, Friday"
        elif day_lower in ['fri', 'friday']:
            return "Monday, Wednesday, Friday"
        # TTh pattern: if any of Tue, Thu, return both
        elif day_lower in ['tue', 'tuesday']:
            return "Tuesday, Thursday"
        elif day_lower in ['thu', 'thursday']:
            return "Tuesday, Thursday"
        # Otherwise return as-is (for other days like Sat, Sun)
        return day_str
    
    # Helper function to format time (remove seconds)
    def format_time(time_str):
        """Format time from HH:MM:SS to HH:MM"""
        if not time_str:
            return ""
        # Remove seconds if present
        if len(time_str) >= 8 and time_str.count(':') >= 2:
            return time_str[:5]  # Take HH:MM
        return time_str
    
    # Format response for frontend
    formatted_sections = []
    for section, course, instructor, timeslot, location, section_name in results:
        # Get cluster numbers for this course by joining course_cluster with clusters table
        cluster_numbers = db.query(ClusterDB.cluster_number).join(
            CourseClusterDB, CourseClusterDB.cluster_id == ClusterDB.cluster_id
        ).filter(
            CourseClusterDB.course_id == course.id
        ).all()
        cluster_ids = [c[0] for c in cluster_numbers]  # cluster_ids now contains cluster_number values
        
        # Get enrollment count (taken seats)
        taken_seats = db.query(TakesDB).filter(
            TakesDB.section_id == section.id,
            TakesDB.status.in_(['enrolled', 'completed'])
        ).count()
        
        # Format time slot with day expansion and time formatting
        days = expand_days(timeslot.day_of_week if timeslot else "")
        start_time = format_time(timeslot.start_time) if timeslot and timeslot.start_time else ""
        end_time = format_time(timeslot.end_time) if timeslot and timeslot.end_time else ""
        time = f"{start_time}-{end_time}" if start_time and end_time else ""
        
        # Extract course code from name (first word) or use course ID as fallback
        course_code = str(course.id)
        if course.name and course.name.strip():
            name_parts = course.name.split()
            if name_parts:
                course_code = name_parts[0]
        
        # Format semester and year (e.g., "Fall 2023")
        semester_year = ""
        if timeslot:
            semester_name = timeslot.semester or ""
            year_value = timeslot.year or ""
            if semester_name and year_value:
                semester_year = f"{semester_name} {year_value}"
        
        # Get section letter (A, B, C, etc.) from section_name table
        # If no section_name found, fallback to section ID
        section_letter = section_name.section_name if section_name and section_name.section_name else str(section.id)
        
        formatted_sections.append({
            "id": str(section.id),
            "code": course_code,
            "name": course.name or "",
            "cluster": cluster_ids,
            "section": section_letter,
            "instructor": instructor.name if instructor else "",
            "days": days,
            "time": time,
            "takenSeats": taken_seats,
            "totalSeats": section.capacity or 0,
            "location": location.building_room_name if location else "",
            "duration": section.duration or "",
            "syllabusUrl": section.syllabus_url,
            "instructorBioUrl": instructor.bio_url if instructor else None,
            "credits": course.credits or 0,
            "semester": timeslot.semester if timeslot else "",
            "year": timeslot.year if timeslot else None,
            "semesterYear": semester_year
        })
    
    return formatted_sections

@app.get("/sections/{section_id}", response_model=Section)
async def get_section(section_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a section by its unique ID.
    
    Input:
        section_id (int): The unique identifier of the section.
        db (Session): Database session.
    
    Output:
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
    
    Output:
        Section: The newly created section's details.
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        db_section = SectionDB(**section.model_dump())
        db.add(db_section)
        db.commit()
        db.refresh(db_section)
        return db_section
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.put("/sections/{section_id}", response_model=Section)
async def update_section(section_id: int, updated_section: SectionCreate, db: Session = Depends(get_db)):
    """
    Update an existing section's details in the database.
    
    Input:
        section_id (int): The unique identifier of the section to update.
        updated_section (SectionCreate): The new section data.
        db (Session): Database session.
    
    Output:
        Section: The updated section's details.
    
    Raises:
        HTTPException: If the section is not found, raises a 404 error.
    """
    try:
        section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        for key, value in updated_section.model_dump().items():
            setattr(section, key, value)
        db.commit()
        db.refresh(section)
        return section
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.delete("/sections/{section_id}")
async def delete_section(section_id: int, db: Session = Depends(get_db)):
    """
    Delete a section by its unique ID from the database.
    
    Input:
        section_id (int): The unique identifier of the section to delete.
        db (Session): Database session.
    
    Output:
        dict: A message confirming successful deletion.
    
    Raises:
        HTTPException: If the section is not found, raises a 404 error.
    """
    try:
        section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        db.delete(section)
        db.commit()
        return {"message": "Section deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting section: {str(e)}")

# COURSE ENDPOINTS

@app.get("/courses", response_model=list[Course])
async def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all courses with pagination.
    
    Input:
        skip (int): Number of records to skip, default 0.
        limit (int): Maximum number of records to return, default 100.
        db (Session): Database session.
    
    Output:
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
    
    Output:
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
    
    Output:
        Course: The newly created course's details.
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        db_course = CourseDB(**course.model_dump())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: int, updated_course: CourseCreate, db: Session = Depends(get_db)):
    """
    Update an existing course's details in the database.
    
    Input:
        course_id (int): The unique identifier of the course to update.
        updated_course (CourseCreate): The new course data.
        db (Session): Database session.
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
        Takes: The newly created enrollment record.
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        db_takes = TakesDB(**takes.model_dump())
        db.add(db_takes)
        db.commit()
        db.refresh(db_takes)
        return db_takes
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.delete("/takes/")
async def delete_takes(student_id: int, section_id: int, db: Session = Depends(get_db)):
    """
    Delete a student enrollment record from the database.
    
    Input:
        student_id (int): The unique identifier of the student.
        section_id (int): The unique identifier of the section.
        db (Session): Database session.
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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
    
    Output:
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

# RECOMMENDATION GENERATION ENDPOINT

class GenerateRecommendationRequest(BaseModel):
    student_id: int
    time_preference: str = 'any'  # 'morning', 'afternoon', 'evening', or 'any'
    semester: Optional[str] = 'Fall'
    year: Optional[int] = 2025

@app.post("/recommendations/generate")
async def generate_recommendations(
    request: GenerateRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate recommendations for a specific student with the given time preference.
    This will delete existing recommendations for the student and create new ones.
    
    Input:
        student_id (int): The student ID to generate recommendations for
        time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
        semester (str): Semester ('Fall', 'Spring', 'Summer')
        year (int): Academic year
    
    Output:
        dict: Success message and count of recommendations generated
    """
    if generate_recommendations_for_student is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation service unavailable. Shared module not found. Please check Docker volumes."
        )
    
    try:
        # Validate time preference
        valid_preferences = ['morning', 'afternoon', 'evening', 'any']
        if request.time_preference not in valid_preferences:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time_preference. Must be one of: {valid_preferences}"
            )
    
        # Check if student exists
        student = db.query(StudentDB).filter(StudentDB.student_id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {request.student_id} not found")
    
        # Delete existing recommendations for this student
        existing = db.query(RecommendationResultDB).filter(
            RecommendationResultDB.student_id == request.student_id
        ).all()
        for rec in existing:
            db.delete(rec)
        db.commit()
        
        # Generate new recommendations
        recommendations = generate_recommendations_for_student(
            engine=engine,
            student_id=request.student_id,
            time_preference=request.time_preference,
            current_year=request.year,
            current_semester=request.semester
        )
        
        if not recommendations:
            return {
                "message": f"No recommendations generated for student {request.student_id}",
                "count": 0
            }
        
        # Save recommendations to database
        saved_count = 0
        
        for slot_num, rec in enumerate(recommendations, 1):
            # Get time_slot_id from section
            section_id = int(rec['section_id'])
            section = db.query(SectionDB).filter(SectionDB.id == section_id).first()
            time_slot_id = section.time_slot_id if section else None
            
            # Convert why_recommended list to string
            why_recommended_str = ', '.join(rec.get('why_recommended', []))
            
            result_data = {
                'student_id': request.student_id,
                'course_id': int(rec['course_id']),
                'recommended_section_id': int(rec['section_id']),
                'course_name': rec['course_name'],
                'cluster': rec.get('cluster', ''),
                'credits': int(rec.get('credits', 0)),
                'time_slot': int(time_slot_id) if time_slot_id is not None else None,
                'recommendation_score': str(rec.get('score', '1.0')),
                'why_recommended': why_recommended_str,
                'slot_number': slot_num,
                'model_version': 'semester_scheduler_v1',
                'time_preference': request.time_preference,
                'semester': request.semester,
                'year': request.year
            }
            
            db_recommendation = RecommendationResultDB(**result_data)
            db.add(db_recommendation)
            saved_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully generated {saved_count} recommendations for student {request.student_id}",
            "count": saved_count,
            "time_preference": request.time_preference
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# DRAFT SCHEDULE ENDPOINTS

@app.get("/draft-schedules", response_model=list[DraftSchedule])
async def get_draft_schedules(
    student_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all draft schedules, optionally filtered by student_id.
    
    Input:
        student_id (Optional[int]): Filter by student ID. If not provided, returns all schedules.
        db (Session): Database session.
    
    Output:
        list[DraftSchedule]: List of draft schedules with their section IDs.
    """
    query = db.query(DraftScheduleDB)
    
    if student_id is not None:
        query = query.filter(DraftScheduleDB.student_id == student_id)
    
    schedules = query.order_by(DraftScheduleDB.created_at.desc()).all()
    
    result = []
    for schedule in schedules:
        # Get section IDs for this schedule
        section_ids = db.query(DraftScheduleSectionDB.section_id).filter(
            DraftScheduleSectionDB.draft_schedule_id == schedule.draft_schedule_id
        ).all()
        section_id_list = [sid[0] for sid in section_ids]
        
        result.append({
            "draft_schedule_id": schedule.draft_schedule_id,
            "student_id": schedule.student_id,
            "name": schedule.name,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else "",
            "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
            "section_ids": section_id_list
        })
    
    return result


@app.get("/draft-schedules/{draft_schedule_id}", response_model=DraftSchedule)
async def get_draft_schedule(
    draft_schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific draft schedule by ID.
    
    Input:
        draft_schedule_id (int): The ID of the draft schedule.
        db (Session): Database session.
    
    Output:
        DraftSchedule: The draft schedule with its section IDs.
    
    Raises:
        HTTPException: If the draft schedule is not found, raises a 404 error.
    """
    schedule = db.query(DraftScheduleDB).filter(
        DraftScheduleDB.draft_schedule_id == draft_schedule_id
    ).first()
    
    if schedule is None:
        raise HTTPException(status_code=404, detail="Draft schedule not found")
    
    # Get section IDs for this schedule
    section_ids = db.query(DraftScheduleSectionDB.section_id).filter(
        DraftScheduleSectionDB.draft_schedule_id == schedule.draft_schedule_id
    ).all()
    section_id_list = [sid[0] for sid in section_ids]
    
    return {
        "draft_schedule_id": schedule.draft_schedule_id,
        "student_id": schedule.student_id,
        "name": schedule.name,
        "created_at": schedule.created_at.isoformat() if schedule.created_at else "",
        "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
        "section_ids": section_id_list
    }


@app.post("/draft-schedules/", response_model=DraftSchedule)
async def create_draft_schedule(
    schedule_data: DraftScheduleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new draft schedule.
    
    Input:
        schedule_data (DraftScheduleCreate): The draft schedule data including student_id, name, and section_ids.
        db (Session): Database session.
    
    Output:
        DraftSchedule: The newly created draft schedule.
    
    Raises:
        HTTPException: If student doesn't exist or sections are invalid.
    """
    # Verify student exists
    student = db.query(StudentDB).filter(StudentDB.student_id == schedule_data.student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify all sections exist
    if schedule_data.section_ids:
        existing_sections = db.query(SectionDB.id).filter(
            SectionDB.id.in_(schedule_data.section_ids)
        ).all()
        existing_section_ids = {sid[0] for sid in existing_sections}
        invalid_sections = set(schedule_data.section_ids) - existing_section_ids
        if invalid_sections:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid section IDs: {list(invalid_sections)}"
            )
    
    try:
        # Create draft schedule
        new_schedule = DraftScheduleDB(
            student_id=schedule_data.student_id,
            name=schedule_data.name
        )
        db.add(new_schedule)
        db.flush()  # Get the ID without committing
        
        # Add sections to the schedule
        for section_id in schedule_data.section_ids:
            schedule_section = DraftScheduleSectionDB(
                draft_schedule_id=new_schedule.draft_schedule_id,
                section_id=section_id
            )
            db.add(schedule_section)
        
        db.commit()
        db.refresh(new_schedule)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating draft schedule: {str(e)}")
    
    return {
        "draft_schedule_id": new_schedule.draft_schedule_id,
        "student_id": new_schedule.student_id,
        "name": new_schedule.name,
        "created_at": new_schedule.created_at.isoformat() if new_schedule.created_at else "",
        "updated_at": new_schedule.updated_at.isoformat() if new_schedule.updated_at else None,
        "section_ids": schedule_data.section_ids
    }


@app.put("/draft-schedules/{draft_schedule_id}", response_model=DraftSchedule)
async def update_draft_schedule(
    draft_schedule_id: int,
    schedule_data: DraftScheduleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing draft schedule.
    
    Input:
        draft_schedule_id (int): The ID of the draft schedule to update.
        schedule_data (DraftScheduleUpdate): The updated schedule data.
        db (Session): Database session.
    
    Output:
        DraftSchedule: The updated draft schedule.
    
    Raises:
        HTTPException: If the draft schedule is not found or sections are invalid.
    """
    schedule = db.query(DraftScheduleDB).filter(
        DraftScheduleDB.draft_schedule_id == draft_schedule_id
    ).first()
    
    if schedule is None:
        raise HTTPException(status_code=404, detail="Draft schedule not found")
    
    # Update name if provided
    if schedule_data.name is not None:
        schedule.name = schedule_data.name
    
    # Update sections if provided
    if schedule_data.section_ids is not None:
        # Verify all sections exist
        existing_sections = db.query(SectionDB.id).filter(
            SectionDB.id.in_(schedule_data.section_ids)
        ).all()
        existing_section_ids = {sid[0] for sid in existing_sections}
        invalid_sections = set(schedule_data.section_ids) - existing_section_ids
        if invalid_sections:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid section IDs: {list(invalid_sections)}"
            )
        
        # Delete existing section associations
        db.query(DraftScheduleSectionDB).filter(
            DraftScheduleSectionDB.draft_schedule_id == draft_schedule_id
        ).delete()
        
        # Add new section associations
        for section_id in schedule_data.section_ids:
            schedule_section = DraftScheduleSectionDB(
                draft_schedule_id=draft_schedule_id,
                section_id=section_id
            )
            db.add(schedule_section)
    
    db.commit()
    db.refresh(schedule)
    
    # Get updated section IDs
    section_ids = db.query(DraftScheduleSectionDB.section_id).filter(
        DraftScheduleSectionDB.draft_schedule_id == schedule.draft_schedule_id
    ).all()
    section_id_list = [sid[0] for sid in section_ids]
    
    return {
        "draft_schedule_id": schedule.draft_schedule_id,
        "student_id": schedule.student_id,
        "name": schedule.name,
        "created_at": schedule.created_at.isoformat() if schedule.created_at else "",
        "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
        "section_ids": section_id_list
    }


@app.delete("/draft-schedules/{draft_schedule_id}")
async def delete_draft_schedule(
    draft_schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a draft schedule.
    
    Input:
        draft_schedule_id (int): The ID of the draft schedule to delete.
        db (Session): Database session.
    
    Output:
        dict: Success message.
    
    Raises:
        HTTPException: If the draft schedule is not found, raises a 404 error.
    """
    schedule = db.query(DraftScheduleDB).filter(
        DraftScheduleDB.draft_schedule_id == draft_schedule_id
    ).first()
    
    if schedule is None:
        raise HTTPException(status_code=404, detail="Draft schedule not found")
    
    # Cascade delete will handle draft_schedule_sections automatically
    db.delete(schedule)
    db.commit()
    
    return {"message": "Draft schedule deleted successfully"}


# STATISTICS ENDPOINTS

# Grade to GPA mapping
GRADE_TO_GPA = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0
}

class GPAProgressPoint(BaseModel):
    term: str  # e.g., "2022-Fall"
    year: int
    semester: str
    gpa: float

class CreditsProgress(BaseModel):
    credit_earned: int
    total_credits: int
    remaining: int

class SemesterProgress(BaseModel):
    percentage: float
    days_passed: int
    days_total: int

class CourseCompletionByProgram(BaseModel):
    program: str
    taken: int
    remaining: int
    total: int

class GradeDistribution(BaseModel):
    grade: str
    count: int
    percentage: float

class PerformanceByCourseType(BaseModel):
    course_type: str
    average_gpa: float
    course_count: int

class CreditAccumulation(BaseModel):
    term: str
    year: int
    semester: str
    credits_earned: int
    cumulative_credits: int

class TimeSlotPerformance(BaseModel):
    time_slot: str  # "morning", "afternoon", "evening"
    average_gpa: float
    course_count: int

class CourseLoad(BaseModel):
    term: str
    year: int
    semester: str
    credits: int

class GradeTrendByCourseType(BaseModel):
    term: str
    year: int
    semester: str
    course_type: str
    gpa: float

class PrerequisiteStatus(BaseModel):
    course_id: int
    course_name: str
    prerequisites_completed: int
    prerequisites_total: int
    completion_percentage: float

class CourseDifficultyPerformance(BaseModel):
    course_id: int
    course_name: str
    credits: int
    grade: str
    gpa_value: float

class SemesterPerformanceHeatmap(BaseModel):
    day_of_week: str  # "Monday", "Tuesday", etc.
    time_slot: str  # "morning", "afternoon", "evening"
    average_gpa: float
    course_count: int

class StatisticsResponse(BaseModel):
    gpa_progress: List[GPAProgressPoint]
    credits_progress: CreditsProgress
    semester_progress: SemesterProgress
    course_completion: List[CourseCompletionByProgram]
    grade_distribution: List[GradeDistribution]
    performance_by_course_type: List[PerformanceByCourseType]
    credit_accumulation: List[CreditAccumulation]
    time_slot_performance: List[TimeSlotPerformance]
    course_load: List[CourseLoad]
    grade_trends_by_course_type: List[GradeTrendByCourseType]
    prerequisites_status: List[PrerequisiteStatus]
    course_difficulty_performance: List[CourseDifficultyPerformance]
    semester_performance_heatmap: List[SemesterPerformanceHeatmap]

@app.get("/statistics/{student_id}", response_model=StatisticsResponse)
async def get_student_statistics(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for a student including:
    - GPA progress over time
    - Credits earned and remaining
    - Semester progress
    - Course completion by program
    - Grade distribution
    - Performance by course type
    - Time slot performance
    - Course load per semester
    - Prerequisites completion status
    
    Input:
        student_id (int): The student ID to get statistics for.
        db (Session): Database session.
    
    Output:
        StatisticsResponse: All statistics for the student.
    
    Raises:
        HTTPException: If student not found or database error occurs.
    """
    try:
        # Input validation
        if student_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid student_id")
        
        # Verify student exists
        student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Pre-load all data to avoid N+1 queries
        # Load all takes with related data in one query
        takes_query = db.query(
            TakesDB,
            SectionDB,
            TimeSlotDB,
            CourseDB
        ).join(
            SectionDB, TakesDB.section_id == SectionDB.id
        ).join(
            TimeSlotDB, SectionDB.time_slot_id == TimeSlotDB.time_slot_id
        ).join(
            CourseDB, SectionDB.course_id == CourseDB.id
        ).filter(
            TakesDB.student_id == student_id
        )
        
        # Pre-load course type mappings to avoid N+1 queries
        all_has_courses = db.query(HasCourseDB).all()
        course_type_map = {}
        for has_course in all_has_courses:
            if has_course.courseid not in course_type_map:
                course_type_map[has_course.courseid] = []
            course_type_map[has_course.courseid].append(has_course.prog_name)
        
        # Load all takes data into memory once
        all_takes_data = takes_query.all()
        
        # 1. GPA Progress over time
        gpa_data = []
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                gpa_value = GRADE_TO_GPA[takes.grade]
                term = f"{time_slot.year}-{time_slot.semester}"
                gpa_data.append({
                    "term": term,
                    "year": time_slot.year,
                    "semester": time_slot.semester,
                    "gpa": gpa_value
                })
        
        # Calculate average GPA per term
        term_gpa = {}
        for item in gpa_data:
            term = item["term"]
            if term not in term_gpa:
                term_gpa[term] = {"gpas": [], "year": item["year"], "semester": item["semester"]}
            term_gpa[term]["gpas"].append(item["gpa"])
        
        gpa_progress = []
        for term, data in sorted(term_gpa.items()):
            avg_gpa = sum(data["gpas"]) / len(data["gpas"])
            gpa_progress.append(GPAProgressPoint(
                term=term,
                year=data["year"],
                semester=data["semester"],
                gpa=round(avg_gpa, 2)
            ))
        
        # 2. Credits Progress
        credit_earned = student.credit or 0
        total_credits = 121  # Standard total credits
        remaining = max(0, total_credits - credit_earned)
        
        credits_progress = CreditsProgress(
            credit_earned=credit_earned,
            total_credits=total_credits,
            remaining=remaining
        )
        
        # 3. Semester Progress
        today = date.today()
        # Assume Fall semester: Sept 1 to Dec 20
        semester_start = date(today.year, 9, 1)
        semester_end = date(today.year, 12, 20)
        
        # If we're past December, use next year's dates
        if today > semester_end:
            semester_start = date(today.year + 1, 9, 1)
            semester_end = date(today.year + 1, 12, 20)
        
        days_total = (semester_end - semester_start).days
        days_passed = max(0, min(days_total, (today - semester_start).days))
        percentage = round((days_passed / days_total * 100), 1) if days_total > 0 else 0
        
        semester_progress = SemesterProgress(
            percentage=percentage,
            days_passed=days_passed,
            days_total=days_total
        )
        
        # 4. Course Completion by Program
        # Get courses student has taken (with completed status) - use pre-loaded data
        student_course_ids = set()
        for takes, section, time_slot, course in all_takes_data:
            if takes.status == "completed":
                student_course_ids.add(section.course_id)
        
        # Get total courses per program - use pre-loaded map
        program_stats = {}
        for course_id, prog_names in course_type_map.items():
            for prog_name in prog_names:
                if prog_name not in program_stats:
                    program_stats[prog_name] = {"total": set(), "taken": 0}
                program_stats[prog_name]["total"].add(course_id)
                if course_id in student_course_ids:
                    program_stats[prog_name]["taken"] += 1
        
        course_completion = []
        for prog_name, stats in program_stats.items():
            total = len(stats["total"])
            taken = stats["taken"]
            remaining = max(0, total - taken)
            
            course_completion.append(CourseCompletionByProgram(
                program=prog_name,
                taken=taken,
                remaining=remaining,
                total=total
            ))
        
        # Sort by program name
        course_completion.sort(key=lambda x: x.program)
        
        # 5. Grade Distribution
        grade_counts = {}
        total_grades = 0
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                grade_counts[takes.grade] = grade_counts.get(takes.grade, 0) + 1
                total_grades += 1
        
        grade_distribution = []
        for grade in ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]:
            count = grade_counts.get(grade, 0)
            percentage = (count / total_grades * 100) if total_grades > 0 else 0
            grade_distribution.append(GradeDistribution(
                grade=grade,
                count=count,
                percentage=round(percentage, 1)
            ))
    
        # 6. Performance by Course Type
        # Get course types from pre-loaded map
        course_type_gpas = {"GENED": [], "BSDS": [], "FND": []}
        
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                gpa_value = GRADE_TO_GPA[takes.grade]
                # Get course type from pre-loaded map
                course_types = course_type_map.get(section.course_id, [])
                for prog_name in course_types:
                    if prog_name in course_type_gpas:
                        course_type_gpas[prog_name].append(gpa_value)
        
        performance_by_course_type = []
        for course_type, gpas in course_type_gpas.items():
            if gpas:
                avg_gpa = sum(gpas) / len(gpas)
                performance_by_course_type.append(PerformanceByCourseType(
                    course_type=course_type,
                    average_gpa=round(avg_gpa, 2),
                    course_count=len(gpas)
                ))
        
        # 7. Credit Accumulation Over Time
        # Get all completed courses with credits
        credit_accumulation_data = {}
        cumulative_credits = 0
        
        for takes, section, time_slot, course in all_takes_data:
            if takes.status == "completed":
                term = f"{time_slot.year}-{time_slot.semester}"
                if term not in credit_accumulation_data:
                    credit_accumulation_data[term] = {
                        "year": time_slot.year,
                        "semester": time_slot.semester,
                        "credits": 0
                    }
                credit_accumulation_data[term]["credits"] += course.credits
        
        credit_accumulation = []
        for term in sorted(credit_accumulation_data.keys()):
            data = credit_accumulation_data[term]
            cumulative_credits += data["credits"]
            credit_accumulation.append(CreditAccumulation(
                term=term,
                year=data["year"],
                semester=data["semester"],
                credits_earned=data["credits"],
                cumulative_credits=cumulative_credits
            ))
        
        # 8. Time Slot Performance
        def get_time_slot_category(start_time: str) -> str:
            """Categorize time slot as morning, afternoon, or evening"""
            if not start_time:
                return "unknown"
            try:
                # Parse time (format: "HH:MM" or "HH:MM:SS")
                hour = int(start_time.split(":")[0])
                if hour < 12:
                    return "morning"
                elif hour < 17:
                    return "afternoon"
                else:
                    return "evening"
            except (ValueError, IndexError):
                return "unknown"
        
        time_slot_performance = {"morning": [], "afternoon": [], "evening": []}
        
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                gpa_value = GRADE_TO_GPA[takes.grade]
                time_category = get_time_slot_category(time_slot.start_time)
                if time_category in time_slot_performance:
                    time_slot_performance[time_category].append(gpa_value)
        
        time_slot_perf_list = []
        for time_slot, gpas in time_slot_performance.items():
            if gpas:
                avg_gpa = sum(gpas) / len(gpas)
                time_slot_perf_list.append(TimeSlotPerformance(
                    time_slot=time_slot,
                    average_gpa=round(avg_gpa, 2),
                    course_count=len(gpas)
                ))
        
        # 9. Course Load Per Semester
        course_load_data = {}
        for takes, section, time_slot, course in all_takes_data:
            term = f"{time_slot.year}-{time_slot.semester}"
            if term not in course_load_data:
                course_load_data[term] = {
                    "year": time_slot.year,
                    "semester": time_slot.semester,
                    "credits": 0
                }
            course_load_data[term]["credits"] += course.credits
        
        course_load = []
        for term in sorted(course_load_data.keys()):
            data = course_load_data[term]
            course_load.append(CourseLoad(
                term=term,
                year=data["year"],
                semester=data["semester"],
                credits=data["credits"]
            ))
        
        # 10. Grade Trends by Course Type
        grade_trends = {}
        
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                gpa_value = GRADE_TO_GPA[takes.grade]
                term = f"{time_slot.year}-{time_slot.semester}"
                # Get course type from pre-loaded map
                course_types = course_type_map.get(section.course_id, [])
                for course_type in course_types:
                    if course_type in ["GENED", "BSDS", "FND"]:
                        key = f"{term}-{course_type}"
                        if key not in grade_trends:
                            grade_trends[key] = {
                                "term": term,
                                "year": time_slot.year,
                                "semester": time_slot.semester,
                                "course_type": course_type,
                                "gpas": []
                            }
                        grade_trends[key]["gpas"].append(gpa_value)
        
        grade_trends_list = []
        for key, data in sorted(grade_trends.items()):
            avg_gpa = sum(data["gpas"]) / len(data["gpas"])
            grade_trends_list.append(GradeTrendByCourseType(
                term=data["term"],
                year=data["year"],
                semester=data["semester"],
                course_type=data["course_type"],
                gpa=round(avg_gpa, 2)
            ))
        
        # 11. Prerequisites Completion Status
        # Get all courses student hasn't taken yet
        all_courses = db.query(CourseDB).all()
        # student_course_ids already computed above
        
        prerequisites_status = []
        for course in all_courses:
            if course.id not in student_course_ids:
                # Get prerequisites for this course
                prereqs = db.query(PrerequisitesDB).filter(
                    PrerequisitesDB.course_id == course.id
                ).all()
                
                if prereqs:
                    total_prereqs = len(prereqs)
                    completed_prereqs = sum(1 for prereq in prereqs if prereq.prerequisite_id in student_course_ids)
                    completion_pct = (completed_prereqs / total_prereqs * 100) if total_prereqs > 0 else 0
                    
                    prerequisites_status.append(PrerequisiteStatus(
                        course_id=course.id,
                        course_name=course.name,
                        prerequisites_completed=completed_prereqs,
                        prerequisites_total=total_prereqs,
                        completion_percentage=round(completion_pct, 1)
                    ))
        
        # Sort by completion percentage (highest first)
        prerequisites_status.sort(key=lambda x: x.completion_percentage, reverse=True)
        # Limit to top 20 to avoid overwhelming the UI
        prerequisites_status = prerequisites_status[:20]
    
        # 12. Course Difficulty vs Performance
        course_difficulty = []
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                course_difficulty.append(CourseDifficultyPerformance(
                    course_id=course.id,
                    course_name=course.name,
                    credits=course.credits,
                    grade=takes.grade,
                    gpa_value=GRADE_TO_GPA[takes.grade]
                ))
    
        # 13. Semester Performance Heatmap
        heatmap_data = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for takes, section, time_slot, course in all_takes_data:
            if takes.grade and takes.grade in GRADE_TO_GPA:
                gpa_value = GRADE_TO_GPA[takes.grade]
                day = time_slot.day_of_week
                # Map day abbreviations to full names
                day_map = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", 
                          "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
                day_full = day_map.get(day, day)
                time_category = get_time_slot_category(time_slot.start_time)
                
                key = f"{day_full}-{time_category}"
                if key not in heatmap_data:
                    heatmap_data[key] = {
                        "day_of_week": day_full,
                        "time_slot": time_category,
                        "gpas": [],
                        "count": 0
                    }
                heatmap_data[key]["gpas"].append(gpa_value)
                heatmap_data[key]["count"] += 1
        
        semester_heatmap = []
        for key, data in heatmap_data.items():
            if data["gpas"]:
                avg_gpa = sum(data["gpas"]) / len(data["gpas"])
                semester_heatmap.append(SemesterPerformanceHeatmap(
                    day_of_week=data["day_of_week"],
                    time_slot=data["time_slot"],
                    average_gpa=round(avg_gpa, 2),
                    course_count=data["count"]
                ))
        
        return StatisticsResponse(
            gpa_progress=gpa_progress,
            credits_progress=credits_progress,
            semester_progress=semester_progress,
            course_completion=course_completion,
            grade_distribution=grade_distribution,
            performance_by_course_type=performance_by_course_type,
            credit_accumulation=credit_accumulation,
            time_slot_performance=time_slot_perf_list,
            course_load=course_load,
            grade_trends_by_course_type=grade_trends_list,
            prerequisites_status=prerequisites_status,
            course_difficulty_performance=course_difficulty,
            semester_performance_heatmap=semester_heatmap
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the error and return 500
        import traceback
        print(f"Error in get_student_statistics: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while calculating statistics: {str(e)}"
        )
