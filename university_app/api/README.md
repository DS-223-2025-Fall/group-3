# API Service

FastAPI-based backend service for the University Course Management System.

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL database (running via Docker Compose)
- Environment variables configured (see `.env` file)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `university_app/` directory with:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/university_db
   ```

3. **Run the development server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Docker

Run via Docker Compose (recommended):
```bash
cd university_app
docker-compose up api
```

## API Endpoints

### Student Endpoints
- `GET /students/{student_id}` - Get student by ID
- `POST /students/` - Create new student
- `PUT /students/{student_id}` - Update student
- `DELETE /students/{student_id}` - Delete student

## Project Structure

```
api/
├── main.py              # FastAPI application and endpoints
├── Database/
│   ├── models.py        # SQLAlchemy database models
│   ├── schema.py        # Pydantic schemas for request/response
│   ├── database.py      # Database connection and session management
│   ├── db_helpers.py    # Reusable CRUD helper functions
│   └── init_db.py       # Database initialization utilities
├── requirements.txt     # Python dependencies
└── Dockerfile           # Docker configuration
```

## Key Features

- **CRUD Operations**: Full Create, Read, Update, Delete for student entities
- **Database Helpers**: Reusable helper functions for common database operations
- **Auto-generated Docs**: FastAPI automatically generates OpenAPI/Swagger documentation
- **Type Safety**: Pydantic schemas for request/response validation
- **Error Handling**: Proper HTTP status codes and error messages

## Database

The API uses SQLAlchemy ORM to interact with PostgreSQL. Database tables are automatically created on startup.

For comprehensive API documentation, see the [MkDocs documentation](../docs/api.md).