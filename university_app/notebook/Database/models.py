"""
Database Models for Notebook - matches ETL models
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True)
    student_name = Column(String)
    credit = Column(Integer)


class Location(Base):
    __tablename__ = "locations"
    
    room_id = Column(Integer, primary_key=True)
    building_room_name = Column(String)


class Instructor(Base):
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    bio_url = Column(String)
    room_id = Column(Integer, ForeignKey('locations.room_id'))


class Department(Base):
    __tablename__ = "departments"
    
    dept_name = Column(String, primary_key=True)
    roomID = Column(Integer, ForeignKey('locations.room_id'))


class Program(Base):
    __tablename__ = "programs"
    
    prog_name = Column(String, primary_key=True)
    deptID = Column(String, ForeignKey('departments.dept_name'))


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    credits = Column(Integer)


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    time_slot_id = Column(Integer, primary_key=True)
    day_of_week = Column(String)
    start_time = Column(String)
    end_time = Column(String)


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer)
    roomID = Column(Integer, ForeignKey('locations.room_id'))
    duration = Column(String)
    year = Column(Integer)
    time_slot_id = Column(Integer, ForeignKey('time_slots.time_slot_id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    syllabus_url = Column(String)


class Prerequisites(Base):
    __tablename__ = "prerequisites"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class Takes(Base):
    __tablename__ = "takes"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    status = Column(String(20))
    grade = Column(String(5), nullable=True)


class Works(Base):
    __tablename__ = "works"
    
    instructorid = Column(Integer, ForeignKey('instructors.id'), primary_key=True)
    dept_name = Column(String, ForeignKey('departments.dept_name'), primary_key=True)


class HasCourse(Base):
    __tablename__ = "hascourse"
    
    prog_name = Column(String, ForeignKey('programs.prog_name'), primary_key=True)
    courseid = Column(Integer, ForeignKey('courses.id'), primary_key=True)


# Model for storing recommender results
class RecommendationResult(Base):
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    recommended_section_id = Column(Integer, ForeignKey('sections.id'))
    recommendation_score = Column(String)  # Store as string to allow flexibility
    model_version = Column(String)  # e.g., 'baseline_v1', 'collaborative_v1'
    created_at = Column(String)  # Timestamp as string for simplicity


# Model for A/B testing assignments
class ABTestAssignment(Base):
    __tablename__ = "ab_test_assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'), unique=True)
    test_group = Column(String)  # 'A' or 'B'
    model_version_a = Column(String)  # Model used for group A
    model_version_b = Column(String)  # Model used for group B
    assigned_at = Column(String)  # Timestamp
