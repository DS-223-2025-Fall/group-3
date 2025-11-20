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
  - `db_helpers.py`: CRUD helper functions for database operations

## Features

### Baseline Recommender System
- Recommends courses based on:
  - Program requirements
  - Prerequisites satisfaction
  - Course popularity
- Uses CRUD helpers (`create_record`) to save recommendations to `recommendation_results` table

### A/B Testing Framework
- Assigns students to test groups (A/B)
- Tracks which model version each student sees
- Uses CRUD helpers (`get_by_id`, `create_record`) to store assignments in `ab_test_assignments` table

## Database Access

**Data Reading:**
- Uses `pd.read_sql_table()` for bulk data loading into pandas DataFrames (efficient for data science workflows)

**Data Writing:**
- Uses CRUD helpers from `Database.db_helpers`:
  - `get_by_id()`: Get single record
  - `create_record()`: Create new records
  - `update_record()`: Update existing records
  - `delete_record()`: Delete records
  - `exists()`: Check if record exists
  - `count_records()`: Count matching records

## Database Tables

The notebook creates two additional tables:
1. `recommendation_results`: Stores recommendation outputs
2. `ab_test_assignments`: Stores A/B test group assignments

These tables are created automatically when you run the "Create Database Tables for Results" cell in the notebook.

## Usage

1. Open the notebook in Jupyter: `http://localhost:8888`
2. Open `baseline_recommender.ipynb`
3. Run cells sequentially to:
   - Load data from database
   - Initialize recommender
   - Generate recommendations
   - Set up A/B testing
   - Save results to database
