# Shared Recommendation Model

This directory contains the production-ready semester recommendation model used by the API.

## Model Overview

The `SemesterScheduler` is a rule-based recommendation system that generates semester course schedules for students based on:

- **Program Requirements**: BSDS sample schedule structure
- **Prerequisites**: Ensures all prerequisite courses are completed
- **Gen-Ed Clusters**: Follows 3-course-per-cluster-group requirement
- **Credit Standing**: Determines student standing (Freshman/Sophomore/Junior/Senior)
- **Time Preferences**: Filters sections by morning/afternoon/evening preference
- **Semester Availability**: Recommends courses available in the next semester

## Model Architecture

### Core Components

1. **`SemesterScheduler`** (`semester_scheduler.py`)
   - Main recommendation engine
   - Rule-based system (no ML training required)
   - Production-ready Python class

2. **`recommender_helpers.py`**
   - Helper functions for data loading
   - `load_data_from_db()`: Loads data from database into pandas DataFrames
   - `generate_recommendations_for_student()`: Main entry point for generating recommendations

## Model Versioning

The model uses semantic versioning tracked in the database:

- **Current Version**: `semester_scheduler_v1`
- **Version Storage**: Stored in `recommendation_results.model_version` column
- **Version Tracking**: All recommendations include model version for traceability

### Version History

- **v1** (`semester_scheduler_v1`): Initial production version
  - BSDS schedule template-based recommendations
  - Gen-Ed cluster group requirements
  - Prerequisite checking
  - Time preference filtering

## Usage in Production

### API Integration

The model is used by the FastAPI backend via:

```python
from shared.recommender_helpers import generate_recommendations_for_student

recommendations = generate_recommendations_for_student(
    engine=engine,
    student_id=student_id,
    time_preference='morning',  # or 'afternoon', 'evening', 'any'
    current_year=2025,
    current_semester='Fall'
)
```

### API Endpoint

**POST** `/recommendations/generate`

Generates recommendations and saves them to the database with model version tracking.

**Request:**
```json
{
  "student_id": 1,
  "time_preference": "morning",
  "semester": "Fall",
  "year": 2025
}
```

**Response:**
```json
{
  "message": "Successfully generated 5 recommendations for student 1",
  "count": 5,
  "time_preference": "morning"
}
```

## Model Logic

### Recommendation Strategy

The model recommends up to 5 courses per semester:

1. **Slots 1-3**: Main courses (Core/Track) from BSDS schedule template
2. **Slot 4**: Gen-Ed course based on remaining cluster requirements
3. **Slot 5**: Foundation course or free elective

### Filtering Rules

1. **Prerequisites**: Only recommends courses where all prerequisites are satisfied
2. **Completion Status**: Excludes already completed or currently enrolled courses
3. **Semester Availability**: Prioritizes courses available in the next semester
4. **Time Preference**: Filters sections by time-of-day when specified

### BSDS Schedule Template

The model follows a predefined 8-semester schedule template based on the BSDS program structure:

- **Semester 1-2**: Freshman courses (CS100, CS111, CS110, etc.)
- **Semester 3-4**: Sophomore courses (CS102, CS107, DS115, etc.)
- **Semester 5-6**: Junior courses (DS110, CS246, DS116, etc.)
- **Semester 7-8**: Senior courses (Track courses, Capstone)

## Model Maintenance

### Updating the Model

Since this is a rule-based system:

1. **Code Changes**: Update `semester_scheduler.py` directly
2. **Version Update**: Increment version in API when deploying changes
3. **Testing**: Test with sample students before production deployment
4. **Documentation**: Update this README with changes

### Model Evaluation

The model can be evaluated by:

- Checking recommendation quality in the database
- Reviewing `why_recommended` field for reasoning
- Comparing recommendations against program requirements
- Student feedback on recommendation relevance

## Dependencies

- `pandas`: Data manipulation
- `sqlalchemy`: Database access
- Standard Python libraries

## File Structure

```
shared/
├── __init__.py                 # Module exports
├── semester_scheduler.py        # Main recommendation engine
├── recommender_helpers.py      # Helper functions
└── README.md                   # This file
```

## Notes

- The model is **stateless** - it doesn't store any trained parameters
- All data is loaded fresh from the database for each recommendation
- The model is **deterministic** - same inputs produce same outputs
- Model version is tracked for audit and debugging purposes

