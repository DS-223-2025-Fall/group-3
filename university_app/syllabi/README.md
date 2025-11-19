# Syllabi Directory

This directory must contain course syllabus PDF files that are served by the API.
If you dont see it, please ask group-3 member to send them.

## File Naming Convention

Syllabi files must follow this naming pattern:
```
course_{course_id}_section_{section_id}.pdf
```

Where:
- `course_id` is the course ID from the database (1-51)
- `section_id` is always `1` (since we have 1 section per course)

**Example:**
- `course_1_section_1.pdf` - Syllabus for course ID 1, section 1
- `course_25_section_1.pdf` - Syllabus for course ID 25, section 1

## How It Works

1. **Docker Volume Mount**: The `syllabi/` directory is mounted into the API container at `/api/syllabi/`
2. **API Endpoint**: Files are served at `http://localhost:8008/syllabi/{filename}`
3. **Database Reference**: The `sections` table stores the `syllabus_url` path (e.g., `/syllabi/course_1_section_1.pdf`)

## Adding Syllabi

1. Place PDF files in this directory (`university_app/syllabi/`)
2. Name them according to the convention: `course_{course_id}_section_1.pdf`
3. Restart the API container if needed: `docker-compose restart api`
4. Access via: `http://localhost:8008/syllabi/course_{course_id}_section_1.pdf`

## Course ID Reference

To find which course_id corresponds to which course, check the database:
```sql
SELECT id, name FROM courses ORDER BY id;
```

Or check the generated CSV file: `etl/data/course.csv`

## Notes

- This directory is **excluded from git** (see `.gitignore`) to avoid committing large PDF files
- For sharing with instructors/PM, use alternative methods (see project documentation)
- The API will return 404 if a syllabus file is missing (this is expected for MVP)

