"""
Streamlit frontend for University Course Management System.

This is a minimal Streamlit layer added to satisfy Milestone 3 requirements.
It uses only built-in Streamlit components and reuses existing FastAPI endpoints.

Note: This does NOT replace or modify the existing React/Vite frontend in app/.
The React app remains the primary UI and is unchanged.
"""

import streamlit as st
import requests
from typing import Optional, List, Dict
from helpers import fetch_sections, API_BASE_URL

# Page configuration
st.set_page_config(
    page_title="University Course Management",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 University Course Management System")
st.markdown("---")

# Sidebar for filters
st.sidebar.header("Filters")

# Year filter
year_options = ["All", "2022", "2023", "2024", "2025"]
selected_year = st.sidebar.selectbox("Year", year_options, index=0)
year_param = None if selected_year == "All" else selected_year

# Semester filter
semester_options = ["All", "Fall", "Spring", "Summer"]
selected_semester = st.sidebar.selectbox("Semester", semester_options, index=0)
semester_param = None if selected_semester == "All" else selected_semester

# Course Type filter
course_type_options = ["All", "GenEd", "Major", "Elective"]
selected_course_type = st.sidebar.selectbox("Course Type", course_type_options, index=0)
course_type_param = None if selected_course_type == "All" else selected_course_type

# Search filter
search_text = st.sidebar.text_input("Search by Course Name", "")

# Main content area
st.header("Course Sections")

# Fetch and display courses
try:
    sections = fetch_sections(
        year=year_param,
        semester=semester_param,
        course_type=course_type_param,
        search=search_text if search_text else None
    )
    
    if not sections:
        st.info("No courses found for the selected filters.")
    else:
        st.success(f"Found {len(sections)} course section(s)")
        
        # Display courses in a table
        # Convert to DataFrame for better display
        import pandas as pd
        
        # Prepare data for display
        display_data = []
        for section in sections:
            display_data.append({
                "Course Code": section.get("code", ""),
                "Course Name": section.get("name", ""),
                "Section": section.get("section", ""),
                "Instructor": section.get("instructor", ""),
                "Days": section.get("days", ""),
                "Time": section.get("time", ""),
                "Location": section.get("location", ""),
                "Credits": section.get("credits", 0),
                "Seats": f"{section.get('takenSeats', 0)}/{section.get('totalSeats', 0)}",
                "Duration": section.get("duration", ""),
                "Clusters": ", ".join([str(c) for c in section.get("cluster", [])]) if section.get("cluster") else "None"
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Expandable section for detailed view
        with st.expander("View Course Details"):
            for idx, section in enumerate(sections):
                st.markdown(f"### {section.get('code', '')} - {section.get('name', '')}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Section:** {section.get('section', '')}")
                    st.write(f"**Instructor:** {section.get('instructor', '')}")
                    st.write(f"**Credits:** {section.get('credits', 0)}")
                with col2:
                    st.write(f"**Days:** {section.get('days', '')}")
                    st.write(f"**Time:** {section.get('time', '')}")
                    st.write(f"**Location:** {section.get('location', '')}")
                with col3:
                    st.write(f"**Seats:** {section.get('takenSeats', 0)}/{section.get('totalSeats', 0)}")
                    st.write(f"**Duration:** {section.get('duration', '')}")
                    clusters = section.get("cluster", [])
                    if clusters:
                        st.write(f"**Clusters:** {', '.join([str(c) for c in clusters])}")
                st.markdown("---")
                
except requests.exceptions.ConnectionError:
    st.error(f"❌ Cannot connect to API at {API_BASE_URL}. Please ensure the API service is running.")
    st.info("💡 Start the API service with: `docker-compose up api` or `docker-compose up -d`")
except Exception as e:
    st.error(f"❌ Error fetching courses: {str(e)}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Streamlit Frontend | API: {}</small>
    </div>
    """.format(API_BASE_URL),
    unsafe_allow_html=True
)

