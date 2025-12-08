"""

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

# Foundation and General Education programs for courses available to all programs
FND_PROGRAM = "FND"      # Foundation program (FND prefix courses)
GENED_PROGRAM = "GENED"  # General Education program (CHSS, CSE courses)

# Department names
DEPARTMENTS = [
    "Manoogian Simone College of Business and Economics",
    "Akian College of Science and Engineering",
    "College of Humanities and Social Sciences",
    "Turpanjian College of Health Sciences",
]

# Mapping course prefixes to programs (using actual program names: BSDS, FND, GENED)
COURSE_PREFIX_TO_PROGRAM = {
    "CS": "BSDS",  # CS courses map to BSDS (data science program)
    "DS": "BSDS",  # DS courses map to BSDS
    "ENGS": "BSDS",  # Engineering courses map to BSDS
    "BUS": "GENED",  # Business courses map to GENED
    "FND": "FND",  # FND courses map to FND
    "CHSS": "FND",  # CHSS courses map to FND (general education)
    "CSE": "BSDS",  # CSE courses map to BSDS
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
    "Business_Analytics": [
        "BUS 101 Introduction to Business",
        "DS 227 Business Analytics for Data Science",
        "DS 206 Business Intelligence",
        "DS 223 Marketing Analytics",
        "DS 207 Time Series Forecasting",
        "CSE 222 Technology Marketing",
    ],
    "Biology_Life_Sciences": [
        "DS 150 Physics & Chemistry in Life Sciences",
        "DS 151 Cell & Molecular Biology",
        "DS 211 Intro to Bioinformatics",
        "DS 215 Systems Biology",
        "DS 213 Computational Biology",
    ],
    "Data_Visualization": ["DS 116 Data Visualization"],
    "Capstone": ["DS 299 Capstone"],
    "Foundation": [
        "FND 101 Freshman Seminar 1",
        "FND 102 Freshman Seminar 2",
        "FND 103 Armenian Language & Literature 1",
        "FND 104 Armenian Language & Literature 2",
        "FND 221 Armenian History 1",
        "FND 222 Armenian History 2",
        "FND 110 Physical Education",
        "FND 152 First Aid",
        "FND 153 Civil Defence",
    ],
    "CHSS": [
        "CHSS 170 Religion in America",
        "CHSS 184 Social Psychology",
        "CHSS 203 Philosophy of Mind",
        "CHSS 205 Learning, activism, and social movements",
        "CHSS 230 Asian Art",
        "CHSS 240 Music and Literature",
        "CHSS 272 Comparative Religion",
        "CHSS 283 Trust",
        "CHSS 296 Special Topics in Social Sciences: Critical Thinking for the Digital Era",
    ],
    "CSE_Other": [
        "CSE 145 Geographic Information Systems",
        "CSE 175 Relativity",
        "CSE 181 Creativity and Technological Innovation",
        "CSE 210 Historical Development of Mathematical Ideas",
    ],
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

# Semester options
SEMESTER_OPTIONS = ['Fall', 'Spring', 'Summer']

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
    """
    Description: Infer a program code from a course name prefix.
    inputs: course_name (str) – full course name (e.g., 'CS 100 Calculus 1').
    return: Program code (str), defaulting to 'BAB' if prefix is unknown.
    """
    parts = course_name.split()
    if len(parts) > 0:
        prefix = parts[0]
        return COURSE_PREFIX_TO_PROGRAM.get(prefix, "BAB")
    return "BAB"


def generate_student(student_id, program_name=None, target_credits=None, name=None):
    """
    Description: Generate a student record with a name, credits, and program name.
    inputs: student_id (int) – sequential student identifier, program_name (str) – program name.
            target_credits (int) – target credit amount (will be updated after takes are generated).
            name (str) – student name (if None, generates random name).
    return: Dict with keys 'id', 'name', 'credit', and 'program_name'.
    """
    if program_name is None:
        program_name = "BSDS"  # For MVP product, lets assume all students are in BSDS program
    
    # If target_credits not specified, assign based on standing distribution
    if target_credits is None:
        # Distribute students across standings: 25% each
        standing_choice = random.choice(["Freshman", "Sophomore", "Junior", "Senior"])
        if standing_choice == "Freshman":
            target_credits = 0
        elif standing_choice == "Sophomore":
            target_credits = 30
        elif standing_choice == "Junior":
            target_credits = 60
        else:  # Senior
            target_credits = 90
    
    # Use provided name or generate random one
    student_name = name if name is not None else fake.name()
    
    return {
        "id": student_id,
        "name": student_name,
        "credit": target_credits,  # Will be updated to match actual completed courses
        "program_name": program_name,
        "_target_credits": target_credits,  # Store target for later use
    }


def generate_location(room_id):
    """
    Description: Generate a location record for a room in Main or PAB.
    inputs: room_id (int) – numeric room identifier (e.g., 101).
    return: Dict with keys 'room_id' and 'building_room_name'.
    """
    building = random.choice(BUILDINGS)
    building_room_name = f"{building} {room_id}"

    return {
        "room_id": room_id,
        "building_room_name": building_room_name,
    }


# AUA faculty instructors
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
    Description: Attach real AUA instructors to random rooms from existing locations.
    inputs: locations (list[dict]) – location records containing 'room_id'.
    return: List of instructor dicts with 'id', 'name', 'bio_url', and 'room_id'.
    """
    room_ids = [loc["room_id"] for loc in locations]
    instructors = []
    for prof in FIXED_INSTRUCTORS:
        instructors.append(
            {
                "id": prof["id"],
                "name": prof["name"],
                "bio_url": prof["bio_url"],
                "room_id": random.choice(room_ids),
            }
        )
    return instructors


def build_course_to_instructor_map():
    """
    Description: Map each course name to an instructor ID, using fixed assignments and random fallback.
    inputs: None; uses global COURSES and FIXED_INSTRUCTORS.
    return: Dict mapping course_name (str) -> instructor_id (int).
    """
    course_to_instructor = {}
    for course_name in COURSES:
        if course_name == "DS 223 Marketing Analytics":
            course_to_instructor[course_name] = 1
        elif course_name == "DS 207 Time Series Forecasting":
            course_to_instructor[course_name] = 3
        elif course_name in (
            "CS 100 Calculus 1",
            "CS 101 Calculus 2",
            "CS 102 Calculus 3",
        ):
            course_to_instructor[course_name] = 2
        elif course_name == "CHSS 203 Philosophy of Mind":
            course_to_instructor[course_name] = 4
        else:
            course_to_instructor[course_name] = random.choice([1, 2, 3, 4])
    return course_to_instructor


def generate_instructor(instructor_id):
    """
    Description: Deprecated random instructor generator; prefer generate_fixed_instructors().
    inputs: instructor_id (int) – identifier for the instructor.
    return: Dict with 'id', 'name', 'bio_url', and 'room_id'.
    """
    first_name = fake.first_name()
    last_name = fake.last_name()
    name = f"{first_name} {last_name}"

    bio_url_patterns = [
        f"https://www.university.edu/faculty/{first_name.lower()}.{last_name.lower()}",
        f"https://www.university.edu/people/{last_name.lower()}-{first_name.lower()}",
        f"https://www.university.edu/instructors/{last_name.lower()}",
        f"https://www.university.edu/department/faculty/{last_name.lower()}",
        f"https://faculty.university.edu/{last_name.lower()}",
    ]
    bio_url = random.choice(bio_url_patterns)

    room_id = random.randint(100, 400)

    return {
        "id": instructor_id,
        "name": name,
        "bio_url": bio_url,
        "room_id": room_id,
    }


def generate_department(dept_name, room_id):
    """
    Description: Generate a department record with a main office location.
    inputs: dept_name (str), room_id (int) for the department office.
    return: Dict with 'dept_name' and 'roomID'.
    """
    return {
        "dept_name": dept_name,
        "roomID": room_id,
    }


def generate_program(prog_name, dept_name):
    """
    Description: Generate a program record for a department program.
    inputs: prog_name (str), dept_name (str).
    return: Dict with 'prog_name' and 'dept_name'.
    """
    return {
        "prog_name": prog_name,
        "dept_name": dept_name,
    }


def generate_course(course_id, course_name):
    """
    Description: Generate a course record with credits.
    inputs: course_id (int), course_name (str).
    return: Dict with 'id', 'name', and 'credits'.
    """
    if (
        "Seminar" in course_name
        or "Physical Education" in course_name
        or "First Aid" in course_name
        or "Civil Defence" in course_name
    ):
        credits = random.choice([1, 2])
    else:
        credits = random.choice([3, 4])

    return {
        "id": course_id,
        "name": course_name,
        "credits": credits,
    }


def generate_time_slot(time_slot_id, day_of_week, start_time, end_time, year, semester):
    """
    Description: Generate a time_slot record with day, formatted start/end times, year, and semester.
    inputs: time_slot_id (int), day_of_week (str), start_time (datetime.time), end_time (datetime.time), year (int), semester (str).
    return: Dict with 'time_slot_id', 'day_of_week', 'start_time', 'end_time', 'year', and 'semester'.
    """
    return {
        "time_slot_id": time_slot_id,
        "day_of_week": day_of_week,
        "start_time": start_time.strftime("%H:%M:%S"),
        "end_time": end_time.strftime("%H:%M:%S"),
        "year": year,
        "semester": semester,
    }


def generate_section(section_id, course_id, instructor_id, room_id, time_slot_id):
    """
    Description: Generate a course section record with fixed capacity and a syllabus URL.
    inputs: section_id, course_id, instructor_id, room_id, time_slot_id (ints).
    return: Dict with section metadata including 'capacity', 'duration', and 'syllabus_url'.
    Note: year and semester are now stored in the time_slot, not in the section.
    """
    capacity = 30
    duration = random.choice(DURATION_OPTIONS)
    syllabus_url = f"/syllabi/course_{course_id}_section_1.pdf"

    return {
        "id": section_id,
        "capacity": capacity,
        "roomID": room_id,
        "duration": duration,
        "time_slot_id": time_slot_id,
        "course_id": course_id,
        "instructor_id": instructor_id,
        "syllabus_url": syllabus_url,
    }


def generate_prerequisites(course_id, prerequisite_id):
    """
    Description: Generate a prerequisites record linking a course to its prerequisite.
    inputs: course_id (int), prerequisite_id (int).
    return: Dict with 'course_id' and 'prerequisite_id'.
    """
    return {
        "course_id": course_id,
        "prerequisite_id": prerequisite_id,
    }


def generate_takes(student_id, section_id, status="enrolled", grade=None):
    """
    Description: Generate a takes record representing a student's enrollment in a section.
    inputs: student_id (int), section_id (int), status (str), grade (str or None).
    return: Dict with 'student_id', 'section_id', 'status', and 'grade'.
    """
    return {
        "student_id": student_id,
        "section_id": section_id,
        "status": status,
        "grade": grade,
    }


def generate_works(dept_name, instructor_id):
    """
    Description: Generate a works record linking an instructor to a department.
    inputs: dept_name (str), instructor_id (int).
    return: Dict with 'dept_name' and 'instructorid'.
    """
    return {
        "dept_name": dept_name,
        "instructorid": instructor_id,
    }


def generate_hascourse(prog_name, course_id):
    """
    Description: Generate a hascourse record linking a program to a course.
    inputs: prog_name (str), course_id (int).
    return: Dict with 'prog_name' and 'courseid'.
    """
    return {
        "prog_name": prog_name,
        "courseid": course_id,
    }


def generate_cluster(cluster_id, cluster_number, theme=None):
    """
    Description: Generate a cluster record for a given cluster number.
    inputs: cluster_id (int), cluster_number (int), theme (str or None).
    return: Dict with cluster metadata including 'theme'.
    """
    return {
        "cluster_id": cluster_id,
        "cluster_number": cluster_number,
        "theme": theme,
    }


def generate_course_cluster(course_id, cluster_id):
    """
    Description: Generate a course_cluster record linking a course to a cluster.
    inputs: course_id (int), cluster_id (int).
    return: Dict with 'course_id' and 'cluster_id'.
    """
    return {
        "course_id": course_id,
        "cluster_id": cluster_id,
    }


def generate_preferred(student_id, course_id):
    """
    Description: Generate a preferred record expressing a student's course preference.
    inputs: student_id (int), course_id (int).
    return: Dict with 'student_id' and 'course_id'.
    """
    return {
        "student_id": student_id,
        "course_id": course_id,
    }


def generate_user(user_id, student_id, username=None, password=None):
    """
    Description: Generate a user record with login credentials linked to a student.
    inputs: user_id (int), student_id (int), username (str or None), password (str or None).
    return: Dict with 'user_id', 'username', 'password', and 'student_id'.
    Note: Password must be unique per model constraint.
    """
    if username is None:
        # Generate username from student name or use pattern
        username = f"student{student_id}"
    
    if password is None:
        # Generate a unique password based on username (in production, this would be hashed)
        password = f"pass_{username}_123"
    
    return {
        "user_id": user_id,
        "username": username,
        "password": password,
        "student_id": student_id,
    }


def generate_section_name(section_name, section_id):
    """
    Description: Generate a section_name record linking a section letter/name to a section.
    inputs: section_name (str) - section letter like 'A', 'B', 'C', etc., section_id (int).
    return: Dict with 'section_name' and 'section_id'.
    """
    return {
        "section_name": section_name,
        "section_id": section_id,
    }


def generate_time_slots():
    """
    Description: Generate all MWF and T/Th time slot records for weekly schedules across all years and semesters.
    inputs: None; uses fixed patterns for days, time ranges, years, and semesters.
    return: List of time_slot dicts with IDs, days, start/end times, year, and semester.
    """
    time_slots = []
    time_slot_id = 1

    # MWF schedule (50-minute classes)
    mwf_days = ["Mon", "Wed", "Fri"]
    mwf_start_times = [
        (8, 30),
        (9, 30),
        (10, 30),
        (11, 30),
        (12, 30),
        (13, 30),
        (14, 30),
        (15, 30),
        (16, 30),
        (17, 30),
        (18, 30),
        (19, 30),
    ]
    mwf_end_times = [
        (9, 20),
        (10, 20),
        (11, 20),
        (12, 20),
        (13, 20),
        (14, 20),
        (15, 20),
        (16, 20),
        (17, 20),
        (18, 20),
        (19, 20),
        (20, 20),
    ]

    # T/Th schedule (75-minute classes)
    tth_days = ["Tue", "Thu"]
    tth_start_times = [
        (9, 0),
        (10, 30),
        (12, 0),
        (13, 30),
        (15, 0),
        (16, 30),
        (18, 0),
        (19, 30),
    ]
    tth_end_times = [
        (10, 15),
        (11, 45),
        (13, 15),
        (14, 45),
        (16, 15),
        (17, 45),
        (19, 15),
        (20, 45),
    ]

    # Generate time slots for each combination of:
    # - Weekly pattern (MWF or T/Th with specific times)
    # - Year (2023, 2024, 2025)
    # - Semester (Fall, Spring, Summer)
    
    # First, collect all weekly patterns
    weekly_patterns = []
    
    # MWF patterns
    for day in mwf_days:
        for i in range(len(mwf_start_times)):
            start_time = time(mwf_start_times[i][0], mwf_start_times[i][1])
            end_time = time(mwf_end_times[i][0], mwf_end_times[i][1])
            weekly_patterns.append((day, start_time, end_time))
    
    # T/Th patterns
    for day in tth_days:
        for i in range(len(tth_start_times)):
            start_time = time(tth_start_times[i][0], tth_start_times[i][1])
            end_time = time(tth_end_times[i][0], tth_end_times[i][1])
            weekly_patterns.append((day, start_time, end_time))
    
    # Generate time slots for each weekly pattern × year × semester combination
    for day, start_time, end_time in weekly_patterns:
        for year in YEAR_OPTIONS:
            for semester in SEMESTER_OPTIONS:
                time_slots.append(generate_time_slot(time_slot_id, day, start_time, end_time, year, semester))
                time_slot_id += 1

    return time_slots


def generate_takes_data(students, sections, courses, prerequisites):
    """
    Description: Generate takes records (enrollments) per student while respecting prerequisites.
    Ensures students have enough completed courses to match their target credit amount.
    inputs: students, sections, courses, prerequisites (lists of dicts as generated above).
    return: List of takes dicts with status/grade, ensuring prerequisite completion logic.
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
    
    # Build course_id to credits mapping
    course_to_credits = {course["id"]: course["credits"] for course in courses}

    grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "P", "NP"]

    for student in students:
        student_id = student["id"]
        completed_courses = set()
        target_credits = student.get("_target_credits", 0)  # Get target credits
        current_credits = 0

        # Shuffle sections for random selection
        available_sections = sections.copy()
        random.shuffle(available_sections)

        # First pass: Generate completed courses until we reach target credits
        for section in available_sections:
            section_id = section["id"]
            course_id = section_to_course[section_id]

            # Check prerequisites
            can_enroll = True
            if course_id in prereq_map:
                required_prereqs = prereq_map[course_id]
                if not all(prereq_id in completed_courses for prereq_id in required_prereqs):
                    can_enroll = False

            if not can_enroll:
                continue

            # If we haven't reached target credits, prioritize completed courses
            if current_credits < target_credits:
                course_credits = course_to_credits.get(course_id, 0)
                # Only add if it won't exceed target by too much (allow some flexibility)
                if current_credits + course_credits <= target_credits + 5:
                    grade = random.choice(grades)
                    takes.append(generate_takes(student_id, section_id, "completed", grade))
                    completed_courses.add(course_id)
                    current_credits += course_credits
                    continue

        # Second pass: Add some enrolled courses (1-3)
        num_enrollments = random.randint(1, 3)
        enrolled_count = 0
        
        for section in available_sections:
            if enrolled_count >= num_enrollments:
                break
                
            section_id = section["id"]
            course_id = section_to_course[section_id]

            # Skip if already completed
            if course_id in completed_courses:
                continue

            # Check prerequisites
            can_enroll = True
            if course_id in prereq_map:
                required_prereqs = prereq_map[course_id]
                if not all(prereq_id in completed_courses for prereq_id in required_prereqs):
                    can_enroll = False

            if not can_enroll:
                continue

            # Add as enrolled
            takes.append(generate_takes(student_id, section_id, "enrolled", None))
            enrolled_count += 1
        
        # Update student's credit field to match actual completed credits
        student["credit"] = current_credits

    return takes


def generate_prerequisites_data(courses):
    """
    Description: Generate a minimal prerequisite set based on course names and simple rules.
    inputs: courses (list[dict]) – course records with 'id' and 'name'.
    return: List of prerequisite dicts produced by generate_prerequisites().
    """
    prerequisites = []
    course_name_to_id = {course["name"]: course["id"] for course in courses}

    # Calculus chain
    if "CS 100 Calculus 1" in course_name_to_id and "CS 101 Calculus 2" in course_name_to_id:
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["CS 101 Calculus 2"],
                course_name_to_id["CS 100 Calculus 1"],
            )
        )

    if "CS 101 Calculus 2" in course_name_to_id and "CS 102 Calculus 3" in course_name_to_id:
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["CS 102 Calculus 3"],
                course_name_to_id["CS 101 Calculus 2"],
            )
        )

    # Numerical Methods needs Linear Algebra
    if "ENGS 211 Numerical Methods" in course_name_to_id and "CS 104 Linear Algebra" in course_name_to_id:
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["ENGS 211 Numerical Methods"],
                course_name_to_id["CS 104 Linear Algebra"],
            )
        )

    # Statistics 1 needs Probability
    if "CS 108 Statistics 1" in course_name_to_id and "CS 107 Probability" in course_name_to_id:
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["CS 108 Statistics 1"],
                course_name_to_id["CS 107 Probability"],
            )
        )

    # Statistics 2 needs Statistics 1
    if "DS 110 Statistics 2" in course_name_to_id and "CS 108 Statistics 1" in course_name_to_id:
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["DS 110 Statistics 2"],
                course_name_to_id["CS 108 Statistics 1"],
            )
        )

    # Programming for Data Science needs CS110
    if (
        "DS 120 Programming for Data Science" in course_name_to_id
        and "CS 110 Intro to Computer Science" in course_name_to_id
    ):
        prerequisites.append(
            generate_prerequisites(
                course_name_to_id["DS 120 Programming for Data Science"],
                course_name_to_id["CS 110 Intro to Computer Science"],
            )
        )

    # Optional advanced prerequisites
    if "CS 251 Machine Learning" in course_name_to_id and "CS 104 Linear Algebra" in course_name_to_id:
        if random.choice([True, False]):
            prerequisites.append(
                generate_prerequisites(
                    course_name_to_id["CS 251 Machine Learning"],
                    course_name_to_id["CS 104 Linear Algebra"],
                )
            )

    if "CS 246 Artificial Intelligence" in course_name_to_id and "CS 111 Discrete Math" in course_name_to_id:
        if random.choice([True, False]):
            prerequisites.append(
                generate_prerequisites(
                    course_name_to_id["CS 246 Artificial Intelligence"],
                    course_name_to_id["CS 111 Discrete Math"],
                )
            )

    return prerequisites


def generate_university_dataset(
    num_students=10,
    num_locations=50,
    num_sections_per_course=1,
    current_year=2025,
):
    """
    Description: Generate a full synthetic university dataset consistent with the ERD.
    inputs: num_students (int), num_locations (int), num_sections_per_course (int), current_year (int).
    return: Dict mapping table names (str) to lists of row dicts (students, courses, sections, etc.).
    """
    # Generate sequential room_ids starting from 1
    room_ids = list(range(1, num_locations + 1))
    locations = [generate_location(room_id) for room_id in room_ids]

    instructors = generate_fixed_instructors(locations)

    course_to_instructor = build_course_to_instructor_map()

    num_instructors = len(instructors)

    courses = []
    for idx, course_name in enumerate(COURSES, start=1):
        courses.append(generate_course(idx, course_name))

    time_slots = generate_time_slots()

    departments = []
    dept_locations = {}
    for i, dept_name in enumerate(DEPARTMENTS):
        room_id = locations[i % len(locations)]["room_id"]
        dept_locations[dept_name] = room_id
        departments.append(generate_department(dept_name, room_id))

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
        "FND": "College of Humanities and Social Sciences",    # Foundation program
        "GENED": "College of Humanities and Social Sciences",  # General Education program
    }

    # All students are assigned to BSDS program
    student_program_map = {}
    bsds_dept_name = program_to_dept["BSDS"]
    fnd_dept_name = program_to_dept["FND"]
    gened_dept_name = program_to_dept["GENED"]
    
    # Create program entries for BSDS, FND, and GENED
    programs.append(generate_program("BSDS", bsds_dept_name))
    programs.append(generate_program("FND", fnd_dept_name))
    programs.append(generate_program("GENED", gened_dept_name))
    
    # Assign all students to BSDS
    for student_id in range(1, num_students + 1):
        student_program_map[student_id] = "BSDS"
    
    # Predefined names for first 5 students (must match usernames)
    predefined_names = ["Armen", "Alla", "Levon", "Marieta", "Yeva"]
    
    # Generate students with their program names (all BSDS)
    # First 5 use predefined names, rest get random names
    students = []
    for i in range(1, num_students + 1):
        if i <= len(predefined_names):
            # Use predefined name for first 5 students
            student_name = predefined_names[i - 1]
        else:
            # Generate random name for remaining students
            student_name = None  # Will be generated by generate_student
        students.append(generate_student(i, "BSDS", name=student_name))

    sections = []
    section_id = 1
    for course in courses:
        instructor_id = course_to_instructor.get(course["name"], 1)
        room_id = random.choice([loc["room_id"] for loc in locations])
        # Select a random time slot (which already includes year and semester)
        time_slot = random.choice(time_slots)
        section = generate_section(
            section_id,
            course["id"],
            instructor_id,
            room_id,
            time_slot["time_slot_id"],
        )
        sections.append(section)
        section_id += 1

    prerequisites = generate_prerequisites_data(courses)

    takes = generate_takes_data(students, sections, courses, prerequisites)
    
    # Clean up temporary _target_credits field from students
    for student in students:
        if "_target_credits" in student:
            del student["_target_credits"]

    works = []

    instructor_to_dept = {}
    instructor_dept_counts = {}

    for course_name, instructor_id in course_to_instructor.items():
        dept_name = None
        for group_name, course_list in COURSE_GROUPS.items():
            if course_name in course_list:
                dept_name = COURSE_GROUP_TO_DEPT.get(group_name, "Akian College of Science and Engineering")
                break

        if not dept_name:
            prefix = course_name.split()[0] if course_name.split() else ""
            if prefix in ["CS", "DS", "ENGS", "CSE"]:
                dept_name = "Akian College of Science and Engineering"
            elif prefix == "BUS":
                dept_name = "Manoogian Simone College of Business and Economics"
            elif prefix in ["CHSS", "FND"]:
                dept_name = "College of Humanities and Social Sciences"
            else:
                dept_name = "Akian College of Science and Engineering"

        if instructor_id not in instructor_dept_counts:
            instructor_dept_counts[instructor_id] = {}
        instructor_dept_counts[instructor_id][dept_name] = (
            instructor_dept_counts[instructor_id].get(dept_name, 0) + 1
        )

    for instructor_id, dept_counts in instructor_dept_counts.items():
        most_common_dept = max(dept_counts.items(), key=lambda x: x[1])[0]
        instructor_to_dept[instructor_id] = most_common_dept

    for instructor_id in range(1, num_instructors + 1):
        dept_name = instructor_to_dept.get(instructor_id, "Akian College of Science and Engineering")
        works.append(generate_works(dept_name, instructor_id))

    hascourse = []
    # For BSDS program: assign first 27 courses (BSDS courses)
    bsds_course_ids = list(range(1, 28))  # Courses 1-27 are BSDS courses
    for course_id in bsds_course_ids:
        hascourse.append(generate_hascourse("BSDS", course_id))
    
    # For FND program: assign FND courses (28-36) - Foundation courses
    fnd_course_ids = list(range(28, 37))  # Courses 28-36 are FND courses
    for course_id in fnd_course_ids:
        hascourse.append(generate_hascourse("FND", course_id))
    
    # For GENED program: assign remaining courses (37-51) - General Education (CHSS, CSE)
    gened_course_ids = list(range(37, len(courses) + 1))  # Courses 37-51
    for course_id in gened_course_ids:
        hascourse.append(generate_hascourse("GENED", course_id))
    
    # Some courses belong to both BSDS and GENED (cross-listed courses)
    # These are typically foundational courses that count toward both major and general education
    # Examples: Calculus, Statistics, Linear Algebra, Intro CS, Discrete Math
    bsds_gened_shared_courses = [
        1,   # CS 100 Calculus 1
        2,   # CS 101 Calculus 2
        3,   # CS 102 Calculus 3
        6,   # CS 111 Discrete Math
        8,   # CS 107 Probability
        9,   # CS 108 Statistics 1
        10,  # DS 110 Statistics 2
        11,  # CS 110 Intro to Computer Science
        16,  # CS 104 Linear Algebra
    ]
    
    # Add these courses to GENED as well (they're already in BSDS)
    for course_id in bsds_gened_shared_courses:
        hascourse.append(generate_hascourse("GENED", course_id))

    clusters = []
    cluster_id = 1
    cluster_descriptions = {
        1: "Arts and Humanities",
        2: "Social Sciences",
        3: "Philosophy and Ethics",
        4: "Social Psychology and Behavior",
        5: "Innovation and Technology",
        6: "Critical Thinking and Analysis",
        7: "Computer Science Foundations",
        8: "Mathematical Sciences",
        9: "Technology and Society",
    }

    # Generate clusters for FND and GENED (general education programs)
    for prog_name in ["FND", "GENED"]:
        for cluster_num in range(1, 7):
            clusters.append(
                generate_cluster(
                    cluster_id,
                    cluster_num,
                    theme=cluster_descriptions.get(cluster_num),
                )
            )
            cluster_id += 1

    # Generate clusters for BSDS (data science program - similar to CS)
    for cluster_num in [5, 7, 8, 9]:
        clusters.append(
            generate_cluster(
                cluster_id,
                cluster_num,
                theme=cluster_descriptions.get(cluster_num),
            )
        )
        cluster_id += 1

    cluster_lookup = {}
    for cluster in clusters:
        key = cluster["cluster_number"]
        cluster_lookup[key] = cluster["cluster_id"]

    course_clusters = []
    course_name_to_id = {course["name"]: course["id"] for course in courses}

    for course in courses:
        course_id = course["id"]
        course_name = course["name"]
        
        # Use COURSES_WITH_CLUSTERS mapping directly instead of reading from course
        if course_name in COURSES_WITH_CLUSTERS:
            cluster_numbers = COURSES_WITH_CLUSTERS[course_name]

            for cluster_num in cluster_numbers:
                cluster_id_found = cluster_lookup.get(cluster_num)
                if cluster_id_found:
                    course_clusters.append(generate_course_cluster(course_id, cluster_id_found))

    preferred = []
    for student in students:
        student_id = student["id"]
        num_preferences = random.randint(1, 3)
        available_courses = courses.copy()
        random.shuffle(available_courses)

        for course in available_courses[:num_preferences]:
            preferred.append(
                generate_preferred(
                    student_id,
                    course["id"],
                )
            )

    # Generate users - create 10 users (5 predefined + 5 random) linked to all students
    users = []
    predefined_usernames = ["Armen", "Alla", "Levon", "Marieta", "Yeva"]
    
    # Generate usernames for all students first, then update student names to match
    usernames_list = []
    for i, student in enumerate(students):
        if i < len(predefined_usernames):
            # First 5: use predefined username
            username = predefined_usernames[i]
        else:
            # Remaining 5: generate username from random name (first initial + last name)
            random_name = fake.name()
            name_parts = random_name.split()
            if len(name_parts) >= 2:
                first_initial = name_parts[0][0].lower()
                last_name = name_parts[-1].lower()
                username = f"{first_initial}{last_name}"
            else:
                username = f"student{i + 1}"
        
        # Ensure username is unique and within 50 char limit
        base_username = username[:50]
        final_username = base_username
        counter = 1
        while final_username in usernames_list:
            suffix = str(counter)
            max_base_len = 50 - len(suffix)
            final_username = f"{base_username[:max_base_len]}{suffix}"
            counter += 1
        
        usernames_list.append(final_username)
    
    # Now update student names to match usernames and create users
    for i, (student, username) in enumerate(zip(students, usernames_list)):
        student_id = student["id"]
        # Update student name to match username (capitalize first letter)
        student["name"] = username.capitalize()
        users.append(generate_user(i + 1, student_id, username=username))

    # Generate section names - assign section letters (A, B, C, etc.) to sections
    section_names = []
    section_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for i, section in enumerate(sections):
        section_id = section["id"]
        # Assign section letter based on index (cycle through A-J)
        section_letter = section_letters[i % len(section_letters)]
        section_names.append(generate_section_name(section_letter, section_id))

    return {
        "student": students,
        "location": locations,
        "instructor": instructors,
        "department": departments,
        "program": programs,
        "course": courses,
        "time_slot": time_slots,
        "section": sections,
        "section_name": section_names,
        "prerequisites": prerequisites,
        "takes": takes,
        "works": works,
        "hascourse": hascourse,
        "cluster": clusters,
        "course_cluster": course_clusters,
        "preferred": preferred,
        "users": users,
    }


if __name__ == "__main__":
    dataset = generate_university_dataset(
        num_students=10,
        num_locations=50,
        num_sections_per_course=1,
        current_year=2025,
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
    