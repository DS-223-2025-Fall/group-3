from Database.models import StudentDB, Base #TODO: add later
from Database.schema import Student, StudentCreate #TODO: add later 
from Database.database import get_db, engine

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
    Description:
        Initializes the database on application startup.
    Inputs:
        None.
    Return:
        Creates all database tables before the API begins serving requests.
    """
    Base.metadata.create_all(bind=engine)

# STUDENT ENDPOINTS

# GET Request - Retrieve a student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Description:
        Retrieves a student's information using their ID.
    Inputs:
        student_id (int): Unique ID of the student.
        db (Session): Active database session.
    Return:
        Student object if found; otherwise raises a 404 error.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# POST Request - Create a new student
@app.post("/students/", response_model=Student)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Description:
        Creates a new student record in the database.
    Inputs:
        student (StudentCreate): Incoming student data.
        db (Session): Active database session.
    Return:
        The newly created student object.
    """
    db_student = StudentDB(
        student_name=student.student_name,
        credit=student.credit
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# PUT - Update a student

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, updated_student: StudentCreate, db: Session = Depends(get_db)):
    """
    Description:
        Updates an existing student's data.
    Inputs:
        student_id (int): ID of the student to update.
        updated_student (StudentCreate): New data for the student.
        db (Session): Active database session.
    Return:
        Updated student object, or 404 if the student does not exist.
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
    Description:
        Deletes a student by ID from the database.
    Inputs:
        student_id (int): Unique ID of the student to remove.
        db (Session): Active database session.
    Return:
        Confirmation message if deletion is successful.
    """
    student = db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

#TODO: add others as well
