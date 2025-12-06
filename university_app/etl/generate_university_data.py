"""
ETL Script for Generating and Loading University Data into a Database.

This script generates data for students, instructors, courses, departments, sections, etc.
and saves the data to CSV files according to the ERD.

Modules:
    - Database.university_data_generator: Functions to generate university data.
    - pandas: For data manipulation and storage in CSV.
    - loguru: For logging.
"""

import pandas as pd
from loguru import logger
import os
from Database.university_data_generator import generate_university_dataset

# Configuration
NUM_STUDENTS = 10
NUM_LOCATIONS = 50
NUM_SECTIONS_PER_COURSE = 1
CURRENT_YEAR = 2025


def main():
    """
    Description: Generate the university dataset, write each table to CSV, and print a summary with sample records.
    inputs: None (uses module-level configuration constants).
    return: None.
    """
    logger.info("Starting university data generation...")

    # Generate the dataset
    dataset = generate_university_dataset(
        num_students=NUM_STUDENTS,
        num_locations=NUM_LOCATIONS,
        num_sections_per_course=NUM_SECTIONS_PER_COURSE,
        current_year=CURRENT_YEAR,
    )

    # Create output directory
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # Save each table to CSV
    tables = [
        "student",
        "location",
        "instructor",
        "department",
        "program",
        "course",
        "time_slot",
        "section",
        "section_name",
        "prerequisites",
        "takes",
        "works",
        "hascourse",
        "cluster",
        "course_cluster",
        "preferred",
        "users",
    ]

    for table_name in tables:
        df = pd.DataFrame(dataset[table_name])
        csv_path = f"{output_dir}/{table_name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df)} {table_name} records to {csv_path}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("DATA GENERATION SUMMARY")
    print("=" * 60)
    print(f"Students: {len(dataset['student'])}")
    print(f"Locations: {len(dataset['location'])}")
    print(f"Instructors: {len(dataset['instructor'])}")
    print(f"Departments: {len(dataset['department'])}")
    print(f"Programs: {len(dataset['program'])}")
    print(f"Courses: {len(dataset['course'])}")
    print(f"Time Slots: {len(dataset['time_slot'])}")
    print(f"Sections: {len(dataset['section'])}")
    print(f"Prerequisites: {len(dataset['prerequisites'])}")
    print(f"Enrollments (takes): {len(dataset['takes'])}")
    print(f"Instructor-Department (works): {len(dataset['works'])}")
    print(f"Program-Course (hascourse): {len(dataset['hascourse'])}")
    print(f"Clusters: {len(dataset['cluster'])}")
    print(f"Course-Cluster: {len(dataset['course_cluster'])}")
    print(f"Preferred (student preferences): {len(dataset['preferred'])}")
    print(f"Users: {len(dataset['users'])}")
    print(f"Section Names: {len(dataset['section_name'])}")

    # Show sample data
    print("\n" + "=" * 60)
    print("SAMPLE RECORDS")
    print("=" * 60)

    if len(dataset["student"]) > 0:
        print("\n--- Sample Student ---")
        sample_student = dataset["student"][0]
        print(f"ID: {sample_student['id']}")
        print(f"Name: {sample_student['name']}")
        print(f"Credits: {sample_student['credit']}")
        print(f"Program Name: {sample_student['program_name']}")

    if len(dataset["course"]) > 0:
        print("\n--- Sample Course ---")
        sample_course = dataset["course"][0]
        print(f"ID: {sample_course['id']}")
        print(f"Name: {sample_course['name']}")
        print(f"Credits: {sample_course['credits']}")

    if len(dataset["instructor"]) > 0:
        print("\n--- Sample Instructor ---")
        sample_instructor = dataset["instructor"][0]
        print(f"ID: {sample_instructor['id']}")
        print(f"Name: {sample_instructor['name']}")
        print(f"Bio URL: {sample_instructor['bio_url']}")
        print(f"Room ID: {sample_instructor['room_id']}")

    if len(dataset["section"]) > 0:
        print("\n--- Sample Section ---")
        sample_section = dataset["section"][0]
        print(f"ID: {sample_section['id']}")
        print(f"Course ID: {sample_section['course_id']}")
        print(f"Instructor ID: {sample_section['instructor_id']}")
        print(f"Capacity: {sample_section['capacity']}")
        print(f"Duration: {sample_section['duration']}")
        print(f"Time Slot ID: {sample_section['time_slot_id']}")
        print(f"Room ID: {sample_section['roomID']}")

    if len(dataset["time_slot"]) > 0:
        print("\n--- Sample Time Slot ---")
        sample_time_slot = dataset["time_slot"][0]
        print(f"ID: {sample_time_slot['time_slot_id']}")
        print(f"Day: {sample_time_slot['day_of_week']}")
        print(f"Time: {sample_time_slot['start_time']} - {sample_time_slot['end_time']}")
        print(f"Year: {sample_time_slot['year']}")
        print(f"Semester: {sample_time_slot['semester']}")

    if len(dataset["takes"]) > 0:
        print("\n--- Sample Enrollment (takes) ---")
        sample_takes = dataset["takes"][0]
        print(f"Student ID: {sample_takes['student_id']}")
        print(f"Section ID: {sample_takes['section_id']}")
        print(f"Status: {sample_takes['status']}")
        print(f"Grade: {sample_takes['grade']}")

    if len(dataset["users"]) > 0:
        print("\n--- Sample User ---")
        sample_user = dataset["users"][0]
        print(f"User ID: {sample_user['user_id']}")
        print(f"Username: {sample_user['username']}")
        print(f"Password: {sample_user['password']}")
        print(f"Student ID: {sample_user['student_id']}")

    if len(dataset["section_name"]) > 0:
        print("\n--- Sample Section Name ---")
        sample_section_name = dataset["section_name"][0]
        print(f"Section Name: {sample_section_name['section_name']}")
        print(f"Section ID: {sample_section_name['section_id']}")

    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("=" * 60)
    print(f"\nAll CSV files saved to: {output_dir}/")
    print("Files created:")
    for table_name in tables:
        print(f"  - {table_name}.csv")


if __name__ == "__main__":
    main()