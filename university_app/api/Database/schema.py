from pydantic import BaseModel
# Pydantic models for request and response validation
# Pydantic models for request and response validation
class Student(BaseModel):
    """
    Response schemas for student
    """ 

    student_id: int
    student_name: str
    credit: int


    class Config:
        from_attributes = True  # This allows the Pydantic model to work with SQLAlchemy models (Pydantic v2)

class StudentCreate(BaseModel):
    """
    Request schema for creating a student
    """    

    student_name: str
    credit: int = 0 # Default credit value

#TODO: implement the others later

