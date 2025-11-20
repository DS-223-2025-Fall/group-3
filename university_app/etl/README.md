# ETL Service - Data Loading Guide

## Overview

The ETL (Extract, Transform, Load) service is used to generate and load university data into the database. It's typically run once during initial setup or when you need to regenerate/refresh the data.

## When to Use ETL

- Initial database setup
- Regenerating test data
- Refreshing the database with new data
- After database reset

## How to Run ETL (When Needed)

### Option 1:  Run One-Time (Without Uncommenting)

If you just need to run ETL once without modifying docker-compose.yaml:

```bash
# Build and run ETL container temporarily
docker-compose run --rm etl python generate_university_data.py
docker-compose run --rm etl python load_data_to_db.py
```

### Option 2: Run Locally (If You Have Python)

```bash
cd etl
python generate_university_data.py
python load_data_to_db.py
```

## Data Persistence

**Important**: Your data is persisted in the `postgres_data/` volume. Commenting out the ETL service does NOT delete your data. The database continues to run and store all your data.

## Files Generated

The ETL process generates CSV files in `etl/data/`:
- student.csv
- location.csv
- instructor.csv
- department.csv
- program.csv
- course.csv
- time_slot.csv
- section.csv
- prerequisites.csv
- takes.csv
- works.csv
- hascourse.csv

These files are then loaded into the PostgreSQL database.

## Notes

- The ETL service doesn't need to run continuously
- Data persists in PostgreSQL even when ETL is stopped
- You can safely comment out ETL after initial data load
- Uncomment only when you need to regenerate/refresh data

