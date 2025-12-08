"""
Pydantic schema definitions for request and response validation.
Provides data validation schemas for all API endpoints including student, course, and section models.
"""

from pydantic import BaseModel
from typing import Optional

# Pydantic models for request and response validation

# User Schemas
class User(BaseModel):
    """Response schema for user"""
    user_id: int
    username: str
    password: str  # Note: In production, never return password in response
    student_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Request schema for creating a user"""
    username: str
    password: str
    student_id: Optional[int] = None

# Student Schemas
class Student(BaseModel):
    """Response schema for student"""
    student_id: int
    student_name: str
    credit: Optional[int] = None
    program_name: str

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    """Request schema for creating a student"""
    student_name: str
    credit: Optional[int] = None
    program_name: str

# Location Schemas
class Location(BaseModel):
    """Response schema for location"""
    room_id: int
    building_room_name: str

    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    """Request schema for creating a location"""
    building_room_name: str

# Instructor Schemas
class Instructor(BaseModel):
    """Response schema for instructor"""
    id: int
    name: str
    bio_url: Optional[str] = None
    room_id: Optional[int] = None

    class Config:
        from_attributes = True

class InstructorCreate(BaseModel):
    """Request schema for creating an instructor"""
    name: str
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
    dept_name: Optional[str] = None

    class Config:
        from_attributes = True

class ProgramCreate(BaseModel):
    """Request schema for creating a program"""
    prog_name: str
    dept_name: Optional[str] = None

class Course(BaseModel):
    """Response schema for course"""
    id: int
    name: str
    credits: int

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    """Request schema for creating a course"""
    name: str
    credits: int

# TimeSlot Schemas
class TimeSlot(BaseModel):
    """Response schema for time slot"""
    time_slot_id: int
    day_of_week: str
    start_time: str
    end_time: str
    year: int
    semester: str

    class Config:
        from_attributes = True

class TimeSlotCreate(BaseModel):
    """Request schema for creating a time slot"""
    day_of_week: str
    start_time: str
    end_time: str
    year: int
    semester: str

# Section Schemas
class Section(BaseModel):
    """Response schema for section"""
    id: int
    capacity: int
    roomID: int
    duration: Optional[str] = None
    time_slot_id: int
    course_id: int
    instructor_id: int
    syllabus_url: Optional[str] = None

    class Config:
        from_attributes = True

class SectionCreate(BaseModel):
    """Request schema for creating a section"""
    capacity: int
    roomID: int
    duration: Optional[str] = None
    time_slot_id: int
    course_id: int
    instructor_id: int
    syllabus_url: Optional[str] = None

# SectionName Schemas
class SectionName(BaseModel):
    """Response schema for section_name"""
    section_name: str
    section_id: int

    class Config:
        from_attributes = True

class SectionNameCreate(BaseModel):
    """Request schema for creating a section_name"""
    section_name: str
    section_id: int

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
    cluster_number: Optional[int] = None
    theme: Optional[str] = None

    class Config:
        from_attributes = True

class ClusterCreate(BaseModel):
    """Request schema for creating a cluster"""
    cluster_number: Optional[int] = None
    theme: Optional[str] = None

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
    course_id: int

    class Config:
        from_attributes = True

class PreferredCreate(BaseModel):
    """Request schema for creating a preferred record"""
    student_id: int
    course_id: int

# RecommendationResult Schemas
class RecommendationResult(BaseModel):
    """Response schema for recommendation result"""
    id: int
    student_id: int
    course_id: Optional[int] = None
    recommended_section_id: int
    time_slot: Optional[int] = None
    recommendation_score: Optional[str] = None
    why_recommended: Optional[str] = None
    slot_number: Optional[int] = None
    model_version: Optional[str] = None
    time_preference: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    course_name: Optional[str] = None
    cluster: Optional[str] = None
    credits: Optional[int] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class RecommendationResultCreate(BaseModel):
    """Request schema for creating a recommendation result"""
    student_id: int
    course_id: Optional[int] = None
    recommended_section_id: int
    time_slot: Optional[int] = None
    recommendation_score: Optional[str] = None
    why_recommended: Optional[str] = None
    slot_number: Optional[int] = None
    model_version: Optional[str] = None
    time_preference: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    course_name: Optional[str] = None
    cluster: Optional[str] = None
    credits: Optional[int] = None

# Draft Schedule Schemas
class DraftSchedule(BaseModel):
    """Response schema for draft schedule"""
    draft_schedule_id: int
    student_id: int
    name: str
    created_at: str
    updated_at: Optional[str] = None
    section_ids: list[int] = []  # List of section IDs in this schedule

    class Config:
        from_attributes = True

class DraftScheduleCreate(BaseModel):
    """Request schema for creating a draft schedule"""
    student_id: int
    name: str
    section_ids: list[int]  # List of section IDs to include in the schedule

class DraftScheduleUpdate(BaseModel):
    """Request schema for updating a draft schedule"""
    name: Optional[str] = None
    section_ids: Optional[list[int]] = None  # Replace all sections with this list