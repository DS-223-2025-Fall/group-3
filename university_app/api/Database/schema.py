from pydantic import BaseModel
# Pydantic models for request and response validation
# Pydantic models for request and response validation
class Student(BaseModel):
    """
    Description:
        Response schema representing a student returned from the database.
    Inputs:
        Automatically populated from SQLAlchemy model attributes.
    Return:
        A validated student object containing ID, name, and credit information.
    """

    student_id: int
    student_name: str
    credit: int


    class Config:
        from_attributes = True  # This allows the Pydantic model to work with SQLAlchemy models (Pydantic v2)

class StudentCreate(BaseModel):
    """
    Description:
        Request schema for creating a new student record.
    Inputs:
        Student name and optionally initial credit value.
    Return:
        A validated object used to insert a new student into the database.
    """   

    student_name: str
    credit: int = 0 # Default credit value

#TODO: implement the others later

