"""
University Data Generator - Updated according to ERD.

Generates data for:
- Students (10 students, credits 0-100)
- Programs (9 programs with shortcut names)
- Departments (4 specific departments)
- Locations (Main and PAB buildings, rooms 100-400)
- Instructors (random names with bio URLs)
- Courses (from provided list)
- Sections (capacity 30, duration 6/8/12 weeks, year 2023/2024/2025)
- Time slots (MWF schedule pattern)
- Prerequisites (specific course prerequisites)
- Junction tables: takes, works, hascourse
"""

from faker import Faker
import random
from datetime import time

fake = Faker()

# Provided course list
COURSES = [
    "CS 100 Calculus 1",
    "CS 101 Calculus 2",
    "CS 102 Calculus 3",
    "ENGS 211 Numerical Methods",
    "DS 299 Capstone",
    "CS 111 Discrete Math",
    "BUS 101 Introduction to Business",
    "CS 107 Probability",
    "CS 108 Statistics 1",
    "DS 110 Statistics 2",
    "CS 110 Intro to Computer Science",
    "DS 120 Programming for Data Science",
    "DS 115 Data Structures / Algorithms for Data Science",
    "DS 205 Databases and Distributed Systems",
    "CS 246 Artificial Intelligence",
    "CS 104 Linear Algebra",
    "DS 150 Physics & Chemistry in Life Sciences",
    "DS 116 Data Visualization",
    "CS 251 Machine Learning",
    "DS 151 Cell & Molecular Biology",
    "DS 211 Intro to Bioinformatics",
    "DS 215 Systems Biology",
    "DS 213 Computational Biology",
    "DS 227 Business Analytics for Data Science",
    "DS 206 Business Intelligence",
    "DS 223 Marketing Analytics",
    "DS 207 Time Series Forecasting",
    "FND 101 Freshman Seminar 1",
    "FND 102 Freshman Seminar 2",
    "FND 103 Armenian Language & Literature 1",
    "FND 104 Armenian Language & Literature 2",
    "FND 221 Armenian History 1",
    "FND 222 Armenian History 2",
    "FND 110 Physical Education",
    "FND 152 First Aid",
    "FND 153 Civil Defence",
    "CHSS 170 Religion in America",
    "CHSS 184 Social Psychology",
    "CHSS 203 Philosophy of Mind",
    "CHSS 205 Learning, activism, and social movements",
    "CHSS 230 Asian Art",
    "CHSS 240 Music and Literature",
    "CHSS 272 Comparative Religion",
    "CHSS 283 Trust",
    "CHSS 296 Special Topics in Social Sciences: Critical Thinking for the Digital Era",
    "CSE 110 Introduction to Computer Science",
    "CSE 145 Geographic Information Systems",
    "CSE 175 Relativity",
    "CSE 181 Creativity and Technological Innovation",
    "CSE 210 Historical Development of Mathematical Ideas",
    "CSE 222 Technology Marketing",
]

# Program names (using shortcut names)
PROGRAMS = [
    "BAB",   # Bachelor of Arts in Business
    "BAEC",  # Bachelor of Arts in English and Communications
    "BAPG",  # Bachelor of Arts in Politics and Governance
    "BSCS",  # Bachelor of Science in Computer Science
    "BSDS",  # Bachelor of Science in Data Science
    "BSES",  # Bachelor of Science in Engineering Sciences
    "BSN",   # Bachelor of Science in Nursing
    "BSESS", # Bachelor of Science in Environmental and Sustainability Sciences
    "BSE",   # Bachelor of Science in Economics
]

# Department names
DEPARTMENTS = [
    "Manoogian Simone College of Business and Economics",
    "Akian College of Science and Engineering",
    "College of Humanities and Social Sciences",
    "Turpanjian College of Health Sciences",
]

# Mapping course prefixes to programs
COURSE_PREFIX_TO_PROGRAM = {
    "CS": "BSCS",   # Computer Science courses -> BSCS
    "DS": "BSDS",   # Data Science courses -> BSDS
    "ENGS": "BSES", # Engineering Sciences courses -> BSES
    "BUS": "BAB",   # Business courses -> BAB
    "FND": "BAB",   # Foundation courses -> BAB (general foundation)
    "CHSS": "BAEC", # CHSS courses -> BAEC (can also map to BAPG, using BAEC as default)
    "CSE": "BSCS",  # CSE courses -> BSCS
}

# Course groupings for instructor assignment
COURSE_GROUPS = {
    "Calculus": ["CS 100 Calculus 1", "CS 101 Calculus 2", "CS 102 Calculus 3"],
    "Probability_Statistics": ["CS 107 Probability", "CS 108 Statistics 1", "DS 110 Statistics 2"],
    "Numerical_Linear": ["ENGS 211 Numerical Methods", "CS 104 Linear Algebra"],
    "Discrete_Math": ["CS 111 Discrete Math"],
    "Intro_CS": ["CS 110 Intro to Computer Science", "CSE 110 Introduction to Computer Science"],
    "Data_Science_Programming": ["DS 120 Programming for Data Science"],
    "Data_Structures_Algorithms": ["DS 115 Data Structures / Algorithms for Data Science"],
    "Databases": ["DS 205 Databases and Distributed Systems"],
    "AI_ML": ["CS 246 Artificial Intelligence", "CS 251 Machine Learning"],
    "Business_Analytics": ["BUS 101 Introduction to Business", "DS 227 Business Analytics for Data Science", 
                          "DS 206 Business Intelligence", "DS 223 Marketing Analytics", 
                          "DS 207 Time Series Forecasting", "CSE 222 Technology Marketing"],
    "Biology_Life_Sciences": ["DS 150 Physics & Chemistry in Life Sciences", "DS 151 Cell & Molecular Biology",
                             "DS 211 Intro to Bioinformatics", "DS 215 Systems Biology", 
                             "DS 213 Computational Biology"],
    "Data_Visualization": ["DS 116 Data Visualization"],
    "Capstone": ["DS 299 Capstone"],
    "Foundation": ["FND 101 Freshman Seminar 1", "FND 102 Freshman Seminar 2",
                   "FND 103 Armenian Language & Literature 1", "FND 104 Armenian Language & Literature 2",
                   "FND 221 Armenian History 1", "FND 222 Armenian History 2",
                   "FND 110 Physical Education", "FND 152 First Aid", "FND 153 Civil Defence"],
    "CHSS": ["CHSS 170 Religion in America", "CHSS 184 Social Psychology", "CHSS 203 Philosophy of Mind",
             "CHSS 205 Learning, activism, and social movements", "CHSS 230 Asian Art",
             "CHSS 240 Music and Literature", "CHSS 272 Comparative Religion", "CHSS 283 Trust",
             "CHSS 296 Special Topics in Social Sciences: Critical Thinking for the Digital Era"],
    "CSE_Other": ["CSE 145 Geographic Information Systems", "CSE 175 Relativity",
                  "CSE 181 Creativity and Technological Innovation", 
                  "CSE 210 Historical Development of Mathematical Ideas"],
}

# Map course groups to departments
COURSE_GROUP_TO_DEPT = {
    "Calculus": "Akian College of Science and Engineering",
    "Probability_Statistics": "Akian College of Science and Engineering",
    "Numerical_Linear": "Akian College of Science and Engineering",
    "Discrete_Math": "Akian College of Science and Engineering",
    "Intro_CS": "Akian College of Science and Engineering",
    "Data_Science_Programming": "Akian College of Science and Engineering",
    "Data_Structures_Algorithms": "Akian College of Science and Engineering",
    "Databases": "Akian College of Science and Engineering",
    "AI_ML": "Akian College of Science and Engineering",
    "Business_Analytics": "Manoogian Simone College of Business and Economics",
    "Biology_Life_Sciences": "Akian College of Science and Engineering",
    "Data_Visualization": "Akian College of Science and Engineering",
    "Capstone": "Akian College of Science and Engineering",
    "Foundation": "College of Humanities and Social Sciences",
    "CHSS": "College of Humanities and Social Sciences",
    "CSE_Other": "Akian College of Science and Engineering",
}

# Building names
BUILDINGS = ["Main", "PAB"]

# Duration options for sections
DURATION_OPTIONS = ["6 weeks", "8 weeks", "12 weeks"]

# Year options for sections
YEAR_OPTIONS = [2023, 2024, 2025]

# Courses with cluster numbers - mapping course name to list of possible cluster numbers
COURSES_WITH_CLUSTERS = {
    "CHSS 170 Religion in America": [1, 2, 3, 4, 6],
    "CHSS 184 Social Psychology": [3, 4, 6],
    "CHSS 203 Philosophy of Mind": [3, 6],
    "CHSS 205 Learning, activism, and social movements": [2, 4, 6],
    "CHSS 230 Asian Art": [1, 2],
    "CHSS 240 Music and Literature": [1],
    "CHSS 272 Comparative Religion": [1, 2, 3, 4, 6],
    "CHSS 283 Trust": [4, 5, 6],
    "CHSS 296 Special Topics in Social Sciences: Critical Thinking for the Digital Era": [1, 4, 6],
    "CSE 110 Introduction to Computer Science": [7, 8, 9],
    "CSE 145 Geographic Information Systems": [7, 8, 9],
    "CSE 175 Relativity": [8],
    "CSE 181 Creativity and Technological Innovation": [5, 9],
    "CSE 210 Historical Development of Mathematical Ideas": [3, 7, 8, 9],
    "CSE 222 Technology Marketing": [5, 9],
}


def get_program_from_course(course_name):
    """Extract program from course name based on prefix."""
    parts = course_name.split()
    if len(parts) > 0:
        prefix = parts[0]
        return COURSE_PREFIX_TO_PROGRAM.get(prefix, "BAB")  # Default to BAB if unknown
    return "BAB"


def generate_student(student_id):
    """Generate a student record - 10 students with credits 0-100. #TODO: MVP - minimal students, can expand in future"""
    return {
        "id": student_id,
        "name": fake.name(),
        "credit": random.randint(0, 100)
    }


def generate_location(room_id):
    """Generate a location record - Main or PAB building, rooms 100-400."""
    building = random.choice(BUILDINGS)
    # Use room_id directly (should be in 100-400 range)
    building_room_name = f"{building} {room_id}"
    
    return {
        "room_id": room_id,
        "building_room_name": building_room_name
    }


# Fixed instructors (AUA faculty)
FIXED_INSTRUCTORS = [
    {
        "id": 1,
        "name": "Karen Hovhannisyan",
        "bio_url": "https://people.aua.am/team_member/karen-hovhannisyan/",
    },
    {
        "id": 2,
        "name": "Nune Gevorgyan",
        "bio_url": "https://people.aua.am/team_member/nune-gevorgyan-ph-d/",
    },
    {
        "id": 3,
        "name": "Sachin Kumar",
        "bio_url": "https://people.aua.am/team_member/sachin-kumar-phd/",
    },
    {
        "id": 4,
        "name": "Zaruhi Karabekian",
        "bio_url": "https://people.aua.am/team_member/zaruhi-karabekian-phd/",
    },
]


def generate_fixed_instructors(locations):
    """
    Use the real AUA instructors with real bios.
    Assign each to a random existing room_id from locations.
    
    Args:
        locations: List of location dictionaries
    
    Returns:
        List of instructor dictionaries with room_id assigned
    """
    room_ids = [loc["room_id"] for loc in locations]
    instructors = []
    for prof in FIXED_INSTRUCTORS:
        instructors.append({
            "id": prof["id"],
            "name": prof["name"],
            "bio_url": prof["bio_url"],
            "room_id": random.choice(room_ids),
        })
    return instructors


def build_course_to_instructor_map():
    """
    Map each course (by name) to one of the fixed instructors:
    - Karen Hovhannisyan (id: 1) -> DS 223 Marketing Analytics
    - Sachin Kumar (id: 3) -> DS 207 Time Series Forecasting
    - Nune Gevorgyan (id: 2) -> CS 100/101/102 (Calculus 1/2/3)
    - Zaruhi Karabekian (id: 4) -> CHSS 203 Philosophy of Mind
    - All other courses -> random one of the four
    
    Returns:
        Dictionary mapping course name to instructor ID
    """
    course_to_instructor = {}
    for course_name in COURSES:
        if course_name == "DS 223 Marketing Analytics":
            course_to_instructor[course_name] = 1  # Karen
        elif course_name == "DS 207 Time Series Forecasting":
            course_to_instructor[course_name] = 3  # Sachin
        elif course_name in (
            "CS 100 Calculus 1",
            "CS 101 Calculus 2",
            "CS 102 Calculus 3",
        ):
            course_to_instructor[course_name] = 2  # Nune
        elif course_name == "CHSS 203 Philosophy of Mind":
            course_to_instructor[course_name] = 4  # Zaruhi
        else:
            # For all remaining courses, just reuse any of the four instructors
            course_to_instructor[course_name] = random.choice([1, 2, 3, 4])
    return course_to_instructor


def generate_instructor(instructor_id):
    """
    DEPRECATED: Use generate_fixed_instructors() instead.
    This function is kept for backward compatibility but should not be used.
    """
    first_name = fake.first_name()
    last_name = fake.last_name()
    name = f"{first_name} {last_name}"
    
    # Generate random bio URL
    bio_url_patterns = [
        f"https://www.university.edu/faculty/{first_name.lower()}.{last_name.lower()}",
        f"https://www.university.edu/people/{last_name.lower()}-{first_name.lower()}",
        f"https://www.university.edu/instructors/{last_name.lower()}",
        f"https://www.university.edu/department/faculty/{last_name.lower()}",
        f"https://faculty.university.edu/{last_name.lower()}"
    ]
    bio_url = random.choice(bio_url_patterns)
    
    # Random room_id (100-400)
    room_id = random.randint(100, 400)
    
    return {
        "id": instructor_id,
        "name": name,
        "bio_url": bio_url,
        "room_id": room_id
    }


def generate_department(dept_name, room_id):
    """Generate a department record."""
    return {
        "dept_name": dept_name,
        "roomID": room_id
    }


def generate_program(prog_name, dept_name, student_id):
    """Generate a program record."""
    return {
        "prog_name": prog_name,
        "dept_name": dept_name,
        "student_id": student_id
    }


def generate_course(course_id, course_name):
    """Generate a course record from the provided course list."""
    # Determine credits (typically 3 for most courses, 1-2 for seminars/PE) #TODO: MVP - random credits, can make more structured based on actual course requirements in future
    if "Seminar" in course_name or "Physical Education" in course_name or "First Aid" in course_name or "Civil Defence" in course_name:
        credits = random.choice([1, 2])
    else:
        credits = random.choice([3, 4])
    
    # Cluster numbers - courses belong to ALL specified clusters
    # Store as comma-separated string (e.g., "1,2,3,4,6")
    if course_name in COURSES_WITH_CLUSTERS:
        cluster_numbers = COURSES_WITH_CLUSTERS[course_name]
        cluster_number = ",".join(map(str, sorted(cluster_numbers)))  # Sort for consistency
    else:
        cluster_number = None
    
    return {
        "id": course_id,
        "name": course_name,
        "credits": credits,
        "cluster_number": cluster_number
    }


def generate_time_slot(time_slot_id, day_of_week, start_time, end_time):
    """Generate a time_slot record."""
    return {
        "time_slot_id": time_slot_id,
        "day_of_week": day_of_week,
        "start_time": start_time.strftime("%H:%M:%S"),
        "end_time": end_time.strftime("%H:%M:%S")
    }


def generate_section(section_id, course_id, instructor_id, room_id, time_slot_id, year):
    """Generate a section record - capacity 30, duration 6/8/12 weeks, year 2023/2024/2025."""
    capacity = 30  # Always 30 #TODO: MVP - fixed capacity, can vary by course type in future
    duration = random.choice(DURATION_OPTIONS)
    # Syllabus URL path matching Docker volume structure
    # Files will be stored in /api/syllabi/ in the container, served at /syllabi/ endpoint
    # Section number is always 1 since we have 1 section per course #TODO: Maybe in future we can have more
    syllabus_url = f"/syllabi/course_{course_id}_section_1.pdf"
    
    return {
        "id": section_id,
        "capacity": capacity,
        "roomID": room_id,
        "duration": duration,
        "year": year,
        "time_slot_id": time_slot_id,
        "course_id": course_id,
        "instructor_id": instructor_id,
        "syllabus_url": syllabus_url
    }


def generate_prerequisites(course_id, prerequisite_id):
    """Generate a prerequisites record."""
    return {
        "course_id": course_id,
        "prerequisite_id": prerequisite_id
    }


def generate_takes(student_id, section_id, status="enrolled", grade=None):
    """
    Generate a takes record (student enrollment).
    
    Args:
        student_id: Student ID
        section_id: Section ID
        status: Enrollment status ('enrolled', 'completed', 'dropped')
        grade: Grade (e.g., 'A', 'B+', 'F', 'P', 'NP') or None for enrolled courses
    """
    return {
        "student_id": student_id,
        "section_id": section_id,
        "status": status,
        "grade": grade
    }


def generate_works(dept_name, instructor_id):
    """Generate a works record (instructor-department relationship)."""
    return {
        "dept_name": dept_name,
        "instructorid": instructor_id
    }


def generate_hascourse(prog_name, course_id):
    """Generate a hascourse record (program-course relationship)."""
    return {
        "prog_name": prog_name,
        "courseid": course_id
    }


def generate_time_slots():
    """
    Generate time slots for MWF and T/Th schedule patterns.
    Monday, Wednesday, Friday (50-minute classes):
    - 8:30-9:20, 9:30-10:20, 10:30-11:20, 11:30-12:20, 12:30-13:20, 13:30-14:20, 14:30-15:20, 15:30-16:20, 16:30-17:20, 17:30-18:20, 18:30-19:20, 19:30-20:00
    
    Tuesday, Thursday (75-minute classes):
    - 9:00-10:15, 10:30-11:45, 12:00-13:15, 13:30-14:45, 15:00-16:15, 16:30-17:45, 18:00-19:15, 19:30-20:00
    All classes end by 8 PM (20:00)
    """
    time_slots = []
    time_slot_id = 1
    
    # MWF schedule (50-minute classes, starting at :30, ending at :20 of next hour)
    # All classes run until 8 PM
    mwf_days = ["Mon", "Wed", "Fri"]
    mwf_start_times = [
        (8, 30), (9, 30), (10, 30), (11, 30),
        (12, 30), (13, 30), (14, 30), (15, 30),
        (16, 30), (17, 30), (18, 30), (19, 30)
    ]
    mwf_end_times = [
        (9, 20), (10, 20), (11, 20), (12, 20),
        (13, 20), (14, 20), (15, 20), (16, 20),
        (17, 20), (18, 20), (19, 20), (20, 20)  
    ]
    
    for day in mwf_days:
        for i in range(len(mwf_start_times)):
            start_time = time(mwf_start_times[i][0], mwf_start_times[i][1])
            end_time = time(mwf_end_times[i][0], mwf_end_times[i][1])
            time_slots.append(generate_time_slot(time_slot_id, day, start_time, end_time))
            time_slot_id += 1
    
    # T/Th schedule (75-minute classes)
    # Pattern: class 9:00-10:15, break 10:15-10:30, class 10:30-11:45, break 11:45-12:00, etc.
    # All classes end by 8 PM
    tth_days = ["Tue", "Thu"]
    tth_start_times = [
        (9, 0), (10, 30), (12, 0), (13, 30),
        (15, 0), (16, 30), (18, 0), (19, 30)
    ]
    tth_end_times = [
        (10, 15), (11, 45), (13, 15), (14, 45),
        (16, 15), (17, 45), (19, 15), (20, 45)  
    ]
    
    for day in tth_days:
        for i in range(len(tth_start_times)):
            start_time = time(tth_start_times[i][0], tth_start_times[i][1])
            end_time = time(tth_end_times[i][0], tth_end_times[i][1])
            time_slots.append(generate_time_slot(time_slot_id, day, start_time, end_time))
            time_slot_id += 1
    
    return time_slots


def generate_takes_data(students, sections, courses, prerequisites):
    """
    Generate takes (enrollments) data respecting prerequisites.
    
    Logic:
    - Students can enroll in courses with no prerequisites
    - Students can only enroll in courses if they've completed all prerequisites
    - Generate a mix of 'enrolled', 'completed', and 'dropped' statuses
    - Completed courses have grades, enrolled courses don't, dropped courses may have F/NP
    
    Args:
        students: List of student dictionaries
        sections: List of section dictionaries
        courses: List of course dictionaries
        prerequisites: List of prerequisite dictionaries
    
    Returns:
        List of takes dictionaries with status and grade
    """
    takes = []
    
    # Build prerequisite map: course_id -> list of prerequisite course_ids
    prereq_map = {}
    for prereq in prerequisites:
        course_id = prereq["course_id"]
        prereq_id = prereq["prerequisite_id"]
        if course_id not in prereq_map:
            prereq_map[course_id] = []
        prereq_map[course_id].append(prereq_id)
    
    # Build section to course mapping
    section_to_course = {section["id"]: section["course_id"] for section in sections}
    
    # Grade options
    grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "P", "NP"]
    passing_grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "P"]
    
    # For each student, generate enrollments
    for student in students:
        student_id = student["id"]
        completed_courses = set()  # Track courses this student has completed
        
        # Generate 3-8 enrollments per student
        num_enrollments = random.randint(3, 8)
        available_sections = sections.copy()
        random.shuffle(available_sections)
        
        enrollments_created = 0
        
        for section in available_sections:
            if enrollments_created >= num_enrollments:
                break
            
            section_id = section["id"]
            course_id = section_to_course[section_id]
            
            # Check if student can enroll (has prerequisites or no prerequisites needed)
            can_enroll = True
            if course_id in prereq_map:
                # Check if student has completed all prerequisites
                required_prereqs = prereq_map[course_id]
                if not all(prereq_id in completed_courses for prereq_id in required_prereqs):
                    can_enroll = False
            
            if not can_enroll:
                continue
            
            # Determine status and grade
            status_choice = random.choices(
                ["completed", "enrolled", "dropped"],
                weights=[40, 50, 10],  # 40% completed, 50% enrolled, 10% dropped
                k=1
            )[0]
            
            if status_choice == "completed":
                # Completed courses have grades
                grade = random.choice(grades)
                takes.append(generate_takes(student_id, section_id, "completed", grade))
                completed_courses.add(course_id)  # Mark as completed
                enrollments_created += 1
                
            elif status_choice == "enrolled":
                # Enrolled courses don't have grades yet
                takes.append(generate_takes(student_id, section_id, "enrolled", None))
                enrollments_created += 1
                
            elif status_choice == "dropped":
                # Dropped courses may have F or NP, or no grade
                grade_choice = random.choice([None, "F", "NP"])
                takes.append(generate_takes(student_id, section_id, "dropped", grade_choice))
                enrollments_created += 1
    
    return takes


def generate_prerequisites_data(courses):
    """
    Generate prerequisites based on requirements. #TODO: MVP - minimal prerequisite set, can expand with more course dependencies in future
    - Calculus courses have each other as prerequisites
    - Numerical Methods should have Linear Algebra as prerequisite
    - Statistics 1 should have Probability as prerequisite
    - Statistics 2 should have Statistics 1 as prerequisite
    - Programming for Data Science should have CS110 as prerequisite
    """
    prerequisites = []
    course_name_to_id = {course["name"]: course["id"] for course in courses}
    
    # Calculus prerequisites: Calc 2 needs Calc 1, Calc 3 needs Calc 2
    if "CS 100 Calculus 1" in course_name_to_id and "CS 101 Calculus 2" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["CS 101 Calculus 2"],
            course_name_to_id["CS 100 Calculus 1"]
        ))
    
    if "CS 101 Calculus 2" in course_name_to_id and "CS 102 Calculus 3" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["CS 102 Calculus 3"],
            course_name_to_id["CS 101 Calculus 2"]
        ))
    
    # Numerical Methods needs Linear Algebra
    if "ENGS 211 Numerical Methods" in course_name_to_id and "CS 104 Linear Algebra" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["ENGS 211 Numerical Methods"],
            course_name_to_id["CS 104 Linear Algebra"]
        ))
    
    # Statistics 1 needs Probability
    if "CS 108 Statistics 1" in course_name_to_id and "CS 107 Probability" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["CS 108 Statistics 1"],
            course_name_to_id["CS 107 Probability"]
        ))
    
    # Statistics 2 needs Statistics 1
    if "DS 110 Statistics 2" in course_name_to_id and "CS 108 Statistics 1" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["DS 110 Statistics 2"],
            course_name_to_id["CS 108 Statistics 1"]
        ))
    
    # Programming for Data Science needs CS110
    if "DS 120 Programming for Data Science" in course_name_to_id and "CS 110 Intro to Computer Science" in course_name_to_id:
        prerequisites.append(generate_prerequisites(
            course_name_to_id["DS 120 Programming for Data Science"],
            course_name_to_id["CS 110 Intro to Computer Science"]
        ))
    
    # Additional logic: Advanced courses typically need intro courses
    # Machine Learning might need Linear Algebra
    if "CS 251 Machine Learning" in course_name_to_id and "CS 104 Linear Algebra" in course_name_to_id:
        if random.choice([True, False]):  # 50% chance
            prerequisites.append(generate_prerequisites(
                course_name_to_id["CS 251 Machine Learning"],
                course_name_to_id["CS 104 Linear Algebra"]
            ))
    
    # AI might need Discrete Math
    if "CS 246 Artificial Intelligence" in course_name_to_id and "CS 111 Discrete Math" in course_name_to_id:
        if random.choice([True, False]):  # 50% chance
            prerequisites.append(generate_prerequisites(
                course_name_to_id["CS 246 Artificial Intelligence"],
                course_name_to_id["CS 111 Discrete Math"]
            ))
    
    return prerequisites


def generate_university_dataset(
    num_students=10,  # TODO: MVP - minimal students, can expand in future
    num_locations=50,  # TODO: MVP - limited locations, can add more buildings/rooms in future
    num_sections_per_course=1,  # TODO: MVP - 1 section per course, can add multiple sections in future
    current_year=2025
):
    """
    Generate a complete university dataset according to ERD.
    
    Returns a dictionary with all tables as lists of dictionaries.
    """
    # Generate students (10 students, credits 0-100) #TODO: MVP - minimal students
    students = [generate_student(i) for i in range(1, num_students + 1)]
    
    # Generate locations (Main and PAB, rooms 100-400) #TODO: MVP - only 2 buildings, can add more in future
    # Generate unique room IDs in the 100-400 range
    room_ids = random.sample(range(100, 401), min(num_locations, 301))
    locations = [generate_location(room_id) for room_id in room_ids]
    
    # Generate fixed instructors (AUA faculty) #TODO: MVP - using 4 fixed instructors, can add more in future
    instructors = generate_fixed_instructors(locations)
    
    # Build course-to-instructor mapping using fixed instructors
    course_to_instructor = build_course_to_instructor_map()
    
    num_instructors = len(instructors)
    
    # Generate courses from the provided list #TODO: MVP - fixed course list (51 courses), can expand with more courses in future
    courses = []
    for idx, course_name in enumerate(COURSES, start=1):
        courses.append(generate_course(idx, course_name))
    
    # Generate time slots (MWF schedule pattern)
    time_slots = generate_time_slots()
    
    # Generate departments (4 specific departments)
    departments = []
    dept_locations = {}
    for i, dept_name in enumerate(DEPARTMENTS):
        room_id = locations[i % len(locations)]["room_id"]
        dept_locations[dept_name] = room_id
        departments.append(generate_department(dept_name, room_id))
    
    # Generate programs (assign to students and departments) #TODO: MVP - minimal student-program assignments, can expand in future
    # Ensure all students are assigned to at least one program
    programs = []
    program_to_dept = {
        "BAB": "Manoogian Simone College of Business and Economics",
        "BAEC": "College of Humanities and Social Sciences",
        "BAPG": "College of Humanities and Social Sciences",
        "BSCS": "Akian College of Science and Engineering",
        "BSDS": "Akian College of Science and Engineering",
        "BSES": "Akian College of Science and Engineering",
        "BSN": "Turpanjian College of Health Sciences",
        "BSESS": "Akian College of Science and Engineering",
        "BSE": "Manoogian Simone College of Business and Economics",
    }
    
    # First, assign each student to at least one program
    student_program_assigned = set()
    student_id = 1
    for prog_name in PROGRAMS:
        dept_name = program_to_dept[prog_name]
        # Assign program to current student, cycling through all students
        programs.append(generate_program(prog_name, dept_name, student_id))
        student_program_assigned.add(student_id)
        student_id = (student_id % num_students) + 1  # Cycle through students 1-10
    
    # Ensure all students are assigned (if any are missing, assign them to remaining programs)
    unassigned_students = set(range(1, num_students + 1)) - student_program_assigned
    if unassigned_students:
        # Assign remaining students to programs (can have multiple students per program)
        for student_id in unassigned_students:
            # Assign to a random program
            prog_name = random.choice(PROGRAMS)
            dept_name = program_to_dept[prog_name]
            programs.append(generate_program(prog_name, dept_name, student_id))
    
    # Generate sections for each course - exactly 1 section per course #TODO: MVP - 1 section per course, can add multiple sections in future
    sections = []
    section_id = 1
    for course in courses:
        # Get the instructor assigned to this course group
        instructor_id = course_to_instructor.get(course["name"], 1)
        # Use a room_id from existing locations
        room_id = random.choice([loc["room_id"] for loc in locations])
        time_slot = random.choice(time_slots)
        year = random.choice(YEAR_OPTIONS)
        section = generate_section(
            section_id, course["id"], instructor_id,
            room_id, time_slot["time_slot_id"], year
        )
        sections.append(section)
        section_id += 1
    
    # Generate prerequisites #TODO: MVP - minimal prerequisite set
    prerequisites = generate_prerequisites_data(courses)
    
    # Generate takes (student enrollments) with status and grade, respecting prerequisites
    takes = generate_takes_data(students, sections, courses, prerequisites)
    
    # Generate works (instructor-department relationships) #TODO: MVP - 1 department per instructor, can add multiple departments per instructor in future
    # Map each fixed instructor to their department based on their primary courses
    works = []
    
    # Map instructors to departments based on their assigned courses
    # Use the most common department from all courses they teach
    instructor_to_dept = {}
    instructor_dept_counts = {}  # Track department frequency for each instructor
    
    for course_name, instructor_id in course_to_instructor.items():
        # Find which department this course belongs to
        dept_name = None
        for group_name, course_list in COURSE_GROUPS.items():
            if course_name in course_list:
                dept_name = COURSE_GROUP_TO_DEPT.get(group_name, "Akian College of Science and Engineering")
                break
        
        # If not found in groups, use prefix-based mapping
        if not dept_name:
            prefix = course_name.split()[0] if course_name.split() else ""
            if prefix in ["CS", "DS", "ENGS", "CSE"]:
                dept_name = "Akian College of Science and Engineering"
            elif prefix == "BUS":
                dept_name = "Manoogian Simone College of Business and Economics"
            elif prefix in ["CHSS", "FND"]:
                dept_name = "College of Humanities and Social Sciences"
            else:
                dept_name = "Akian College of Science and Engineering"  # Default
        
        # Count departments for each instructor
        if instructor_id not in instructor_dept_counts:
            instructor_dept_counts[instructor_id] = {}
        instructor_dept_counts[instructor_id][dept_name] = instructor_dept_counts[instructor_id].get(dept_name, 0) + 1
    
    # Assign each instructor to their most common department
    for instructor_id, dept_counts in instructor_dept_counts.items():
        # Get the department with the highest count
        most_common_dept = max(dept_counts.items(), key=lambda x: x[1])[0]
        instructor_to_dept[instructor_id] = most_common_dept
    
    # Generate works records for each instructor
    for instructor_id in range(1, num_instructors + 1):
        dept_name = instructor_to_dept.get(instructor_id, "Akian College of Science and Engineering")
        works.append(generate_works(dept_name, instructor_id))
    
    # Generate hascourse (program-course relationships) #TODO: MVP - random assignment, can make more structured/realistic in future
    hascourse = []
    for program in programs:
        prog_name = program["prog_name"]
        # Each program has multiple courses
        num_courses_in_program = random.randint(10, 20)
        program_courses = random.sample(
            range(1, len(courses) + 1),
            min(num_courses_in_program, len(courses))
        )
        for course_id in program_courses:
            hascourse.append(generate_hascourse(prog_name, course_id))
    
    return {
        "student": students,
        "location": locations,
        "instructor": instructors,
        "department": departments,
        "program": programs,
        "course": courses,
        "time_slot": time_slots,
        "section": sections,
        "prerequisites": prerequisites,
        "takes": takes,
        "works": works,
        "hascourse": hascourse,
    }


if __name__ == "__main__":
    # Example: Generate dataset
    dataset = generate_university_dataset(
        num_students=10,
        num_locations=50,
        num_sections_per_course=1,
        current_year=2025
    )
    
    print(f"Generated {len(dataset['student'])} students")
    print(f"Generated {len(dataset['location'])} locations")
    print(f"Generated {len(dataset['instructor'])} instructors")
    print(f"Generated {len(dataset['department'])} departments")
    print(f"Generated {len(dataset['program'])} programs")
    print(f"Generated {len(dataset['course'])} courses")
    print(f"Generated {len(dataset['time_slot'])} time slots")
    print(f"Generated {len(dataset['section'])} sections")
    print(f"Generated {len(dataset['prerequisites'])} prerequisites")
    print(f"Generated {len(dataset['takes'])} student enrollments")
    print(f"Generated {len(dataset['works'])} instructor-department assignments")
    print(f"Generated {len(dataset['hascourse'])} program-course relationships")
