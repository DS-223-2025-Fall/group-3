# University Course Management System

A full-stack application for managing university courses, students, and schedules.

## Architecture

- **Frontend**: React + TypeScript (Vite)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ETL**: Python scripts for data generation and loading
- **Documentation**: MkDocs with Material theme
- **Containerization**: Docker & Docker Compose

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/DS-223-2025-Fall/group-3/tree/main
cd group-3/university_app
```

### 2. Environment Variables

The `.env` file is included in the repository with default configuration. You can use it as-is or modify it if needed:

- **Database Configuration**: Default credentials are set
- **Container Names**: Defaults are provided
- **pgAdmin**: Default admin credentials

If you need to change any values, edit the `.env` file in the `university_app/` directory.

### 3. Start All Services

**On Mac/Linux:**
```bash
docker compose up -d --build
```

**On Windows:**
```cmd
docker compose up -d --build
```

**Note:** This project is fully cross-platform compatible. All scripts work on both Mac and Windows:
- Container scripts (run inside Docker) work on all platforms
- Host scripts: Use `init_db.sh` on Mac/Linux, `init_db.bat` or `init_db.ps1` on Windows

**That's it!** The database will be automatically initialized on first startup:
- Database tables are created automatically
- Data is generated and loaded automatically
- All services will start once initialization is complete

**Note:** The initialization only runs if the database is empty. If you need to regenerate data, see the "Regenerating Data" section below.

This will start:
- PostgreSQL database (port 5432)
- pgAdmin (port 5050)
- FastAPI backend (port 8008)
- React frontend (port 5173)

### 5. Access the Application

- **React Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8008
- **API Docs**: http://localhost:8008/docs
- **pgAdmin**: http://localhost:5050

## Common Commands

All commands work on both Mac/Linux and Windows. Use `docker compose` (with space) for modern Docker Compose, or `docker-compose` (with hyphen) for older versions.

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose down
```

### Access database via psql
```bash
docker compose exec db psql -U postgres -d university_db
```

### Access pgAdmin
- URL: http://localhost:5050
- Email: admin@admin.com
- Password: (from .env file)

### Regenerating Data

If you need to regenerate or reload the database data, you can use the initialization scripts:

**On Mac/Linux:**
```bash
./init_db.sh
```

**On Windows (Command Prompt):**
```cmd
init_db.bat
```

**On Windows (PowerShell):**
```powershell
.\init_db.ps1
```

**Or manually:**
```bash
# Option 1: Clear database and restart (recommended)
docker compose down -v
docker compose up -d --build

# Option 2: Manually run ETL
docker compose run --rm etl bash run_etl.sh
```

**Note:** The initialization scripts will:
1. Stop all containers
2. Remove the database volume (deletes all data)
3. Start the database
4. Run the ETL process to load fresh data

## Documentation

This project uses [MkDocs](https://www.mkdocs.org/) with the Material theme for documentation.

### How to use

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Serve documentation locally** (for development):
   ```bash
   mkdocs serve
   ```
   The documentation will be available at http://127.0.0.1:8000

3. **Build the documentation**:
   ```bash
   mkdocs build
   ```
   This generates static HTML files in the `site/` directory.

### Documentation Structure

- **Configuration**: `mkdocs.yaml` - Main configuration file
- **Source files**: `docs/` directory contains all markdown documentation files
  - `docs/index.md` - Home page
  - `docs/etl.md` - ETL documentation
  - `docs/api.md` - API documentation
  - `docs/app.md` - Frontend app documentation
  - `docs/api_models.md` - API models documentation
- **Build output**: `site/` directory (generated, not committed to git)

### Editing Documentation

Simply edit the markdown files in the `docs/` directory. The changes will be reflected when you rebuild or serve the documentation.

## Notes

- **ETL Service**: Commented out after initial data load to save resources. Uncomment only when needed.
- **Data Persistence**: Database data is stored in `postgres_data/` volume and persists between restarts.
- **Environment Variables**: The `.env` file is included in the repository for easy setup.
