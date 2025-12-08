"""
Database Models for Notebook - matches API models
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from Database.database import Base

class User(Base):
    """
    Database model for User table.
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(70), nullable=False, unique=True)
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=True)


class Student(Base):
    """
    Database model for Student table.
    """
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    credit = Column(Integer, nullable=True)
    program_name = Column(String(100), nullable=False)


class Location(Base):
    """
    Database model for Location table.
    """
    __tablename__ = "locations"
    
    room_id = Column(Integer, primary_key=True)
    building_room_name = Column(String(100), nullable=False)


class Instructor(Base):
    """
    Database model for Instructor table.
    """
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    bio_url = Column(String(255), nullable=True)
    room_id = Column(Integer, ForeignKey('locations.room_id'), nullable=True)


class Department(Base):
    __tablename__ = "departments"
    
    dept_name = Column(String, primary_key=True)
    roomID = Column(Integer, ForeignKey('locations.room_id'))


class Program(Base):
    """
    Database model for Program table.
    """
    __tablename__ = "programs"
    
    prog_name = Column(String, primary_key=True)
    dept_name = Column(String(50), ForeignKey('departments.dept_name'), nullable=True)


class Course(Base):
    """
    Database model for Course table.
    """
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)


class TimeSlot(Base):
    """
    Database model for TimeSlot table.
    """
    __tablename__ = "time_slots"
    
    time_slot_id = Column(Integer, primary_key=True)
    day_of_week = Column(String(3), nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)


class Section(Base):
    """
    Database model for Section table.
    """
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer, nullable=False)
    roomID = Column(Integer, ForeignKey('locations.room_id'), nullable=False)
    duration = Column(String(50))
    time_slot_id = Column(Integer, ForeignKey('time_slots.time_slot_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructors.id'), nullable=False)
    syllabus_url = Column(String(255))


class SectionName(Base):
    """
    Database model for SectionName table.
    """
    __tablename__ = "section_name"
    
    section_name = Column(String, primary_key=True)  # section_letter
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True, nullable=False)


class Prerequisites(Base):
    __tablename__ = "prerequisites"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class Takes(Base):
    __tablename__ = "takes"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    status = Column(String(20))  # e.g., 'enrolled', 'completed', 'dropped'
    grade = Column(String(5), nullable=True)  # e.g., 'A', 'B+', 'F', 'P', 'NP'


class Works(Base):
    __tablename__ = "works"
    
    instructorid = Column(Integer, ForeignKey('instructors.id'), primary_key=True)
    dept_name = Column(String, ForeignKey('departments.dept_name'), primary_key=True)


class HasCourse(Base):
    __tablename__ = "hascourse"
    
    prog_name = Column(String, ForeignKey('programs.prog_name'), primary_key=True)
    courseid = Column(Integer, ForeignKey('courses.id'), primary_key=True)


class Cluster(Base):
    """
    Database model for Cluster table.
    Represents academic clusters (thematic groupings of courses).
    """
    __tablename__ = "clusters"
    
    cluster_id = Column(Integer, primary_key=True)
    cluster_number = Column(Integer, nullable=True)
    theme = Column(String(500), nullable=True)


class CourseCluster(Base):
    """
    Database model for Course-Cluster junction table (many-to-many relationship).
    Links courses to clusters.
    """
    __tablename__ = "course_cluster"
    
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    cluster_id = Column(Integer, ForeignKey('clusters.cluster_id'), primary_key=True)


class Preferred(Base):
    """
    Database model for Preferred table - junction table linking students to courses.
    Represents student preferences for courses.
    """
    __tablename__ = "preferred"
    
    student_id = Column(Integer, ForeignKey('students.student_id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)


# Model for storing recommender results
class RecommendationResult(Base):
    """
    Database model for storing semester recommendation results.
    
    course_id kept as nullable for backward compatibility.
    
    This table stores the output of the semester recommendation system,
    including full semester schedules recommended for students.
    
    Relationships:
    - Links to students (who the recommendation is for)
    - Links to sections (specific section recommended)
    - Links to time_slots (when the section is offered) - updated to FK
    """
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False, index=True)
    # course_id kept as nullable for backward compatibility
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)  # Deprecated: can be derived from section->course
    recommended_section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    time_slot = Column(Integer, ForeignKey('time_slots.time_slot_id'), nullable=True)
    
    # Recommendation metadata
    # course_name, cluster, credits removed - can be derived from section->course relationship
    # Keeping for backward compatibility but marked as deprecated
    course_name = Column(String(200), nullable=True)  # Deprecated: can be derived from section->course
    cluster = Column(String(200), nullable=True)  # Deprecated: can be derived from course_cluster
    credits = Column(Integer, nullable=True)  # Deprecated: can be derived from course
    
    # Recommendation logic
    recommendation_score = Column(String(50), nullable=True)  # Score/ranking (can be string for flexibility)
    why_recommended = Column(Text, nullable=True)  # JSON string or text explaining why this was recommended
    slot_number = Column(Integer, nullable=True)  # Position in semester schedule (1-5)
    
    # Model and context
    model_version = Column(String(50), nullable=True)  # e.g., 'semester_scheduler_v1', 'baseline_v1'
    time_preference = Column(String(20), nullable=True)  # 'morning', 'afternoon', 'evening'
    semester = Column(String(20), nullable=True)  # 'Fall', 'Spring', 'Summer' - kept for backward compatibility
    year = Column(Integer, nullable=True)  # Academic year - kept for backward compatibility
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

