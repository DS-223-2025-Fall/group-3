"""
Database Models for Notebook

Only includes models that are actually used in the notebook.
Other tables are accessed via pandas DataFrames.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from Database.database import Base


class RecommendationResult(Base):
    """
    Database model for storing semester recommendation results.
    
    This table stores the output of the semester recommendation system,
    including full semester schedules recommended for students.
    
    Relationships:
    - Links to students (who the recommendation is for)
    - Links to sections (specific section recommended)
    - Links to time_slots (when the section is offered)
    """
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)
    recommended_section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    time_slot = Column(Integer, ForeignKey('time_slots.time_slot_id'), nullable=True)
    
    # Recommendation metadata
    course_name = Column(String(200), nullable=True)
    cluster = Column(String(200), nullable=True)
    credits = Column(Integer, nullable=True)
    
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

