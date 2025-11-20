# Data Science Notebook Service

This service provides a Jupyter Notebook environment for data science work, including:
- Schedule Recommender System
- A/B Testing Framework
- Database integration for storing results

## Notebook Structure

- `baseline_recommender.ipynb`: Baseline recommender system and A/B testing framework
- `Database/`: Database connection and models
  - `database.py`: Database connection setup
  - `models.py`: SQLAlchemy models matching the main database schema

## Features

### Baseline Recommender System
- Recommends courses based on:
  - Program requirements
  - Prerequisites satisfaction
  - Course popularity
- Saves recommendations to `recommendation_results` table (TODO)

### A/B Testing Framework
- Assigns students to test groups (A/B)
- Tracks which model version each student sees
- Stores assignments in `ab_test_assignments` table (TODO)

## Database Tables (TODO)

The notebook creates two additional tables:
1. `recommendation_results`: Stores recommendation outputs
2. `ab_test_assignments`: Stores A/B test group assignments

These tables are created automatically when you run the notebook cell that calls `Base.metadata.create_all()`.

## Usage

1. Open the notebook in Jupyter: `http://localhost:8888`
2. Open `baseline_recommender.ipynb`
3. Run cells sequentially to:
   - Load data from database
   - Initialize recommender
   - Generate recommendations
   - Set up A/B testing
   - Save results to database
