# University Course Management System

A full-stack application for managing university courses, students, and schedules.

## Architecture

- **Frontend**: React + TypeScript (Vite)
- **Streamlit Frontend**: Minimal Streamlit layer (Milestone 3 requirement)
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

```bash
docker-compose up -d --build
```

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

## How to Run Streamlit Frontend

A minimal Streamlit frontend has been added to satisfy Milestone 3 requirements. This does **not** replace or modify the existing React frontend - both can run independently.

### Prerequisites

1. Ensure the API service is running (see "Quick Start" section above)
2. Python 3.8+ installed
3. Streamlit dependencies installed

### Installation

1. **Navigate to the Streamlit app directory:**
   ```bash
   cd university_app/streamlit_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install globally:
   ```bash
   pip install streamlit requests pandas
   ```

### Running the Streamlit App

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Access the Streamlit frontend:**
   - The app will automatically open in your browser at http://localhost:8501
   - If it doesn't open automatically, navigate to the URL shown in the terminal

### Configuration

The Streamlit app connects to the FastAPI backend at `http://localhost:8008` by default.

To use a different API URL, set the environment variable:
```bash
export STREAMLIT_API_URL=http://your-api-url:8008
streamlit run app.py
```

### Features

The Streamlit frontend provides:
- Course section browsing with filters (Year, Semester, Course Type, Search)
- Course details display in table format
- Expandable detailed view for each course
- Uses only built-in Streamlit components (no third-party UI libraries)

**Note:** The Streamlit frontend is minimal and uses default Streamlit styling. The primary UI remains the React frontend, which is unchanged.

### Regenerating Data

If you need to regenerate or reload the database data:

```bash
# Option 1: Clear database and restart (recommended)
docker-compose down
rm -rf postgres_data/
docker-compose up -d --build

# Option 2: Manually run ETL
docker-compose run --rm etl bash run_etl.sh
```

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
