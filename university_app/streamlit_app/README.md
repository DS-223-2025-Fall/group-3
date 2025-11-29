# Streamlit Frontend

This directory contains a minimal Streamlit frontend added to satisfy Milestone 3 requirements.

## Important Notes

- **This does NOT replace or modify the existing React/Vite frontend** in `../app/`
- The React app remains the primary UI and is completely unchanged
- This Streamlit layer uses only built-in Streamlit components (no third-party UI libraries)
- All functionality reuses existing FastAPI endpoints

## Files

- `app.py` - Main Streamlit application entrypoint
- `helpers.py` - Helper functions to interact with FastAPI backend
- `requirements.txt` - Python dependencies for Streamlit app

## Running

See the main README.md in the repository root for detailed instructions.

Quick start:
```bash
cd university_app/streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

The app will be available at http://localhost:8501

## API Connection

The Streamlit app connects to the FastAPI backend at `http://localhost:8008` by default.

To use a different API URL:
```bash
export STREAMLIT_API_URL=http://your-api-url:8008
streamlit run app.py
```

## Features

- Course section browsing with filters (Year, Semester, Course Type, Search)
- Course details displayed in table format
- Expandable detailed view for each course
- Uses only built-in Streamlit components

