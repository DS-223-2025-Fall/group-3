"""
Database Models for Notebook - matches ETL models
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    credit = Column(Integer, default=0)
    program_name = Column(String(100), nullable=False)


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
    year = Column(Integer)
    semester = Column(String)  # e.g., 'Fall', 'Spring', 'Summer'


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer)
    roomID = Column(Integer, ForeignKey('locations.room_id'))
    duration = Column(String)
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
    Database model for Cluster table - weak entity (depends on Program).
    Represents academic clusters within programs.
    """
    __tablename__ = "clusters"
    
    cluster_id = Column(Integer, primary_key=True)
    cluster_number = Column(Integer, nullable=False)  # e.g., 1, 2, 3, 4, 5, 6, 7, 8, 9
    prog_name = Column(String, ForeignKey('programs.prog_name'), nullable=False)  # Weak entity dependency
    description = Column(String, nullable=True)  # Optional description of the cluster


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
    
    This table stores the output of the semester recommendation system,
    including full semester schedules recommended for students.
    
    Relationships:
    - Links to students (who the recommendation is for)
    - Links to courses (what course was recommended)
    - Links to sections (specific section recommended)
    """
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    recommended_section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    
    # Recommendation metadata
    course_name = Column(String(200), nullable=False)  # Store course name for quick access
    cluster = Column(String(200))  # Cluster(s) this course belongs to
    credits = Column(Integer)  # Number of credits for this course
    time_slot = Column(String(100))  # Human-readable time slot (e.g., "Mon 08:30-09:20")
    
    # Recommendation logic
    recommendation_score = Column(String(50))  # Score/ranking (can be string for flexibility)
    why_recommended = Column(Text)  # JSON string or text explaining why this was recommended
    slot_number = Column(Integer)  # Position in semester schedule (1-5)
    
    # Model and context
    model_version = Column(String(50))  # e.g., 'semester_scheduler_v1', 'baseline_v1'
    time_preference = Column(String(20))  # 'morning', 'afternoon', 'evening'
    semester = Column(String(20))  # 'Fall', 'Spring', 'Summer'
    year = Column(Integer)  # Academic year
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Model for A/B testing assignments
class ABTestAssignment(Base):
    """
    Database model for A/B testing assignments.
    
    Tracks which students are assigned to which test groups
    for comparing different UI element positions and configurations.
    """
    __tablename__ = "ab_test_assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id'), unique=True, nullable=False, index=True)
    
    # Test group assignment
    test_group = Column(String(1), nullable=False)  # 'A' or 'B'
    
    # UI Element Positions (stored as JSON string)
    # Format: {"search_bar": "top", "dropdowns": "left", "buttons": "right", "header_color": "blue"}
    ui_config = Column(Text)  # JSON string with UI element positions
    
    # Timestamp
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Model for UI element click tracking
class UIElementClick(Base):
    """
    Database model for tracking clicks on UI elements.
    
    Tracks which UI elements users click on and their positions
    to determine optimal UI layouts.
    
    Connected to ab_test_assignments because:
    - The element_position is determined by the test assignment's ui_config
    - We need to analyze clicks by test group (A or B)
    - Clicks are a direct result of the A/B test assignment
    """
    __tablename__ = "ui_element_clicks"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Foreign key to ab_test_assignments (primary relationship)
    assignment_id = Column(Integer, ForeignKey('ab_test_assignments.id'), nullable=False, index=True)
    
    # Keep student_id for convenience (can also get via assignment.student_id)
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False, index=True)
    
    # UI element information
    element_type = Column(String(50), nullable=False)  # 'search_bar', 'dropdown', 'button', 'slider', etc.
    element_id = Column(String(100))  # Specific element identifier (e.g., 'search_button', 'year_dropdown')
    element_position = Column(String(50))  # Position variant (e.g., 'top', 'left', 'right', 'bottom')
    
    # Click metadata
    click_count = Column(Integer, default=1)  # Number of clicks (can aggregate)
    page_url = Column(String(500))  # URL where click occurred
    
    # Timestamp
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
