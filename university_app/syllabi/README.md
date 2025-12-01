# Syllabi Directory

This directory must contain a zip file (`syllabi.zip`) with all course syllabus PDF files.
The zip file will be automatically extracted when the API container starts via Docker Compose.

If you don't see the zip file, please ask a group-3 member to send it.

## File Naming Convention

Syllabi files inside the zip must follow this naming pattern:
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

1. **Docker Volume Mount**: The entire `syllabi` directory is mounted into the API container at `/syllabi_source` (read-only). This allows the container to start even if `syllabi.zip` doesn't exist yet.
2. **Automatic Extraction**: On container startup, the entrypoint script checks for `syllabi.zip` in the mounted directory and automatically unzips it to `/api/syllabi/` if found.
3. **API Endpoint**: Files are served at `http://localhost:8008/syllabi/{filename}`
4. **Database Reference**: The `sections` table stores the `syllabus_url` path (e.g., `/syllabi/course_1_section_1.pdf`)

## Adding/Updating Syllabi

1. Create a zip file named `syllabi.zip` containing all PDF files
2. Place the zip file in this directory (`university_app/syllabi/syllabi.zip`)
3. Ensure PDF files inside the zip follow the naming convention: `course_{course_id}_section_1.pdf`
4. Restart the API container: `docker-compose restart api` (or rebuild: `docker-compose up -d --build api`)
5. The zip file will be automatically extracted on container startup
6. Access via: `http://localhost:8008/syllabi/course_{course_id}_section_1.pdf`

## Creating the Zip File

To create the zip file from individual PDF files:
```bash
cd university_app/syllabi
zip syllabi.zip course_*.pdf
```

Or from a directory containing the PDFs:
```bash
cd /path/to/syllabi/pdfs
zip -r syllabi.zip *.pdf
mv syllabi.zip /path/to/university_app/syllabi/
```

## Course ID Reference

To find which course_id corresponds to which course, check the database:
```sql
SELECT id, name FROM courses ORDER BY id;
```

Or check the generated CSV file: `etl/data/course.csv`

## Notes

- The zip file (`syllabi.zip`) is **excluded from git** (see `.gitignore`) to avoid committing large files
- The syllabi directory is mounted as read-only (`:ro`) in docker-compose for safety
- **The container will start successfully even if `syllabi.zip` doesn't exist** - the entrypoint script handles this gracefully
- The extraction happens automatically on container startup (only if the zip file exists and PDFs aren't already extracted)
- For sharing with instructors/PM, use alternative methods (see project documentation)
- The API will return 404 if a syllabus file is missing (this is expected for MVP)

