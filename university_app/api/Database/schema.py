from pydantic import BaseModel
from typing import Optional

# Pydantic models for request and response validation

# Student Schemas
class Student(BaseModel):
    """Response schema for student"""
    student_id: int
    student_name: str
    credit: int

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    """Request schema for creating a student"""
    student_name: str
    credit: int = 0

# Location Schemas
class Location(BaseModel):
    """Response schema for location"""
    room_id: int
    building_room_name: Optional[str] = None

    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    """Request schema for creating a location"""
    building_room_name: Optional[str] = None

# Instructor Schemas
class Instructor(BaseModel):
    """Response schema for instructor"""
    id: int
    name: Optional[str] = None
    bio_url: Optional[str] = None
    room_id: Optional[int] = None

    class Config:
        from_attributes = True

class InstructorCreate(BaseModel):
    """Request schema for creating an instructor"""
    name: Optional[str] = None
    bio_url: Optional[str] = None
    room_id: Optional[int] = None

# Department Schemas
class Department(BaseModel):
    """Response schema for department"""
    dept_name: str
    roomID: Optional[int] = None

    class Config:
        from_attributes = True

class DepartmentCreate(BaseModel):
    """Request schema for creating a department"""
    dept_name: str
    roomID: Optional[int] = None

# Program Schemas
class Program(BaseModel):
    """Response schema for program"""
    prog_name: str
    deptID: Optional[str] = None
    student_id: Optional[int] = None

    class Config:
        from_attributes = True

class ProgramCreate(BaseModel):
    """Request schema for creating a program"""
    prog_name: str
    deptID: Optional[str] = None
    student_id: Optional[int] = None

# Course Schemas
class Course(BaseModel):
    """Response schema for course"""
    id: int
    name: Optional[str] = None
    credits: Optional[int] = None
    cluster_number: Optional[str] = None

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    """Request schema for creating a course"""
    name: Optional[str] = None
    credits: Optional[int] = None
    cluster_number: Optional[str] = None

# TimeSlot Schemas
class TimeSlot(BaseModel):
    """Response schema for time slot"""
    time_slot_id: int
    day_of_week: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    class Config:
        from_attributes = True

class TimeSlotCreate(BaseModel):
    """Request schema for creating a time slot"""
    day_of_week: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

# Section Schemas
class Section(BaseModel):
    """Response schema for section"""
    id: int
    capacity: Optional[int] = None
    roomID: Optional[int] = None
    duration: Optional[str] = None
    year: Optional[int] = None
    time_slot_id: Optional[int] = None
    course_id: Optional[int] = None
    instructor_id: Optional[int] = None
    syllabus_url: Optional[str] = None

    class Config:
        from_attributes = True

class SectionCreate(BaseModel):
    """Request schema for creating a section"""
    capacity: Optional[int] = None
    roomID: Optional[int] = None
    duration: Optional[str] = None
    year: Optional[int] = None
    time_slot_id: Optional[int] = None
    course_id: Optional[int] = None
    instructor_id: Optional[int] = None
    syllabus_url: Optional[str] = None

# Prerequisites Schemas
class Prerequisites(BaseModel):
    """Response schema for prerequisites"""
    course_id: int
    prerequisite_id: int

    class Config:
        from_attributes = True

class PrerequisitesCreate(BaseModel):
    """Request schema for creating prerequisites"""
    course_id: int
    prerequisite_id: int

# Takes Schemas
class Takes(BaseModel):
    """Response schema for takes (student enrollment)"""
    student_id: int
    section_id: int
    status: Optional[str] = None
    grade: Optional[str] = None

    class Config:
        from_attributes = True

class TakesCreate(BaseModel):
    """Request schema for creating a takes record"""
    student_id: int
    section_id: int
    status: Optional[str] = None
    grade: Optional[str] = None

# Works Schemas
class Works(BaseModel):
    """Response schema for works (instructor-department relationship)"""
    instructorid: int
    dept_name: str

    class Config:
        from_attributes = True

class WorksCreate(BaseModel):
    """Request schema for creating a works record"""
    instructorid: int
    dept_name: str

# HasCourse Schemas
class HasCourse(BaseModel):
    """Response schema for hascourse (program-course relationship)"""
    prog_name: str
    courseid: int

    class Config:
        from_attributes = True

class HasCourseCreate(BaseModel):
    """Request schema for creating a hascourse record"""
    prog_name: str
    courseid: int

# Cluster Schemas
class Cluster(BaseModel):
    """Response schema for cluster"""
    cluster_id: int
    cluster_number: int
    prog_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ClusterCreate(BaseModel):
    """Request schema for creating a cluster"""
    cluster_number: int
    prog_name: str
    description: Optional[str] = None

# CourseCluster Schemas
class CourseCluster(BaseModel):
    """Response schema for course_cluster"""
    course_id: int
    cluster_id: int

    class Config:
        from_attributes = True

class CourseClusterCreate(BaseModel):
    """Request schema for creating a course_cluster record"""
    course_id: int
    cluster_id: int

# Preferred Schemas
class Preferred(BaseModel):
    """Response schema for preferred"""
    student_id: int
    cluster_id: int
    preference_order: Optional[int] = None

    class Config:
        from_attributes = True

class PreferredCreate(BaseModel):
    """Request schema for creating a preferred record"""
    student_id: int
    cluster_id: int
    preference_order: Optional[int] = None