from Database.models import StudentDB, Base #TODO: add later
from Database.schema import Student, StudentCreate #TODO: add later 
from Database.database import get_db, engine

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI(title="University Course Management API")


@app.on_event("startup")
async def startup_event():
    """
    Create database tables on startup.
    This ensures all tables are created when the application starts.
    """
    Base.metadata.create_all(bind=engine)

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
