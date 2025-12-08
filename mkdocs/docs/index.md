# University Course Management System

Full-stack application for managing university courses, schedules, and academic analytics.

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
- **View Statistics**: Access academic performance statistics and analytics with 13+ visualization metrics
- **Save and Manage Schedules**: Save multiple draft schedules for future reference

## Expected Outcomes

- **Streamlined Course Selection**: Students can easily browse and filter courses to find what they need
- **Intelligent Planning**: Automated recommendations help students plan optimal semester schedules
- **Prerequisite Compliance**: System ensures students only see courses they're eligible to take
- **Time Optimization**: Recommendations consider time preferences to build convenient schedules
- **Academic Progress Tracking**: Statistics help students understand their academic performance

## Architecture

- **Frontend**: React + TypeScript (Vite, Tailwind CSS)
- **Backend**: FastAPI (Python) with 50+ REST endpoints
- **Database**: PostgreSQL with 20+ tables
- **ETL**: Data generation and loading pipeline
- **Infrastructure**: Docker & Docker Compose

## Components

- **API**: FastAPI backend with CRUD operations, recommendations, and statistics
- **APP**: React frontend for course browsing and schedule management
- **ETL**: Data generation and database initialization
- **Shared**: Production-ready recommendation engine
- **Notebook**: Jupyter environment for data analysis

## Documentation

- [ETL Documentation](etl.md) - Data generation and loading
- [API Documentation](api.md) - Backend API reference
- [API Models](api_models.md) - Database schema
- [Frontend App](app.md) - React application guide
