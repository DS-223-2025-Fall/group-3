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

### 3. Load Initial Data (First Time Only)

The ETL service doesn't run automatically. You need to load data on first setup:

**Run the ETL script (Recommended)**
```bash
# This runs the complete ETL process: generates data, creates tables, and loads data
docker-compose run --rm etl bash run_etl.sh
```

This will:
- Generate CSV data files
- Create database tables (if they don't exist)
- Load all data into the database

**Note:** The ETL service has `restart: "no"` to save resources. Run it manually whenever you need to regenerate or reload data.

### 4. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- pgAdmin (port 5050)
- FastAPI backend (port 8008)
- React frontend (port 5173)
- Documentation (port 8000)

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8008
- **API Docs**: http://localhost:8008/docs
- **Documentation**: http://localhost:8000
- **pgAdmin**: http://localhost:5050

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Access database via psql
```bash
docker-compose exec db psql -U postgres -d university_db
```

### Access pgAdmin
- URL: http://localhost:5050
- Email: admin@admin.com
- Password: (from .env file)

## Documentation

This project uses [MkDocs](https://www.mkdocs.org/) with the Material theme for documentation.

### Setup Documentation

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```
   Or install MkDocs directly:
   ```bash
   pip install mkdocs mkdocs-material "mkdocstrings[python]"
   ```

2. **Build the documentation**:
   ```bash
   mkdocs build
   ```
   This generates static HTML files in the `site/` directory.

3. **Serve documentation locally** (for development):
   ```bash
   mkdocs serve
   ```
   The documentation will be available at http://127.0.0.1:8000

4. **Or run via Docker** (recommended for consistency):
   ```bash
   cd university_app
   docker-compose up -d docs
   ```
   The documentation will be available at http://localhost:8000

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
