# University App Documentation

Welcome to the University App documentation!

This project is a full-stack university course management and recommendation system built with microservices architecture.

## Problem

Students need an efficient way to browse available courses, plan their semester schedules, and receive personalized course recommendations based on their program requirements, completed prerequisites, and preferences. Manual course selection and schedule planning is time-consuming and error-prone, especially when considering prerequisite chains, program requirements, and time preferences.

## Solution

The University Course Management System is a web application that enables students to:

- **Browse and Search Courses**: Filter courses by year, semester, course type (GenEd, Major, Elective), and search by course name
- **View Course Details**: See instructor information, time slots, locations, seat availability, and syllabus links
- **Create Draft Schedules**: Select courses and build draft semester schedules with conflict detection
- **Get Personalized Recommendations**: Receive rule-based semester course recommendations that consider:
  - Program requirements (BSDS schedule template)
  - Prerequisite completion status
  - Gen-Ed cluster requirements (3 courses per cluster group)
  - Student credit standing (Freshman/Sophomore/Junior/Senior)
  - Time preferences (morning/afternoon/evening)
  - Semester availability
- **View Statistics**: Access academic performance statistics and analytics
- **Save and Manage Schedules**: Save multiple draft schedules for future reference

## Expected Outcomes

- **Streamlined Course Selection**: Students can easily browse and filter courses to find what they need
- **Intelligent Planning**: Automated recommendations help students plan optimal semester schedules
- **Prerequisite Compliance**: System ensures students only see courses they're eligible to take
- **Time Optimization**: Recommendations consider time preferences to build convenient schedules
- **Academic Progress Tracking**: Statistics help students understand their academic performance

## Project Structure

The project consists of several main components:

- **ETL**: Data extraction, transformation, and loading pipeline
- **API**: FastAPI-based backend service
- **APP**: Frontend React application
- **Notebook**: Jupyter notebooks for data analysis and recommendations

## Getting Started

To get started with the project, please refer to the individual component documentation:

- [ETL Documentation](etl.md)
- [API Documentation](api.md)
- [APP Documentation](app.md)
- [API Models Documentation](api_models.md)

