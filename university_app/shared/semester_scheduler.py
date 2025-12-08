"""
Semester Recommendation Scheduler
Shared module for generating course recommendations
"""

import pandas as pd
import os
from datetime import datetime

class SemesterScheduler:
    """
    Production-ready semester recommendation engine that follows:
    - Gen-Ed cluster rules (3 courses from each cluster group)
    - BSDS sample schedule structure
    - Prerequisites
    - Credit standing
    - Time-of-day preferences
    """
    
    def __init__(self, data_dict, current_year=None, current_semester=None):
        self.data = data_dict
        # Use current year from datetime if not provided, or from environment variable
        if current_year is None:
            current_year = int(os.environ.get('CURRENT_YEAR', datetime.now().year))
        self.current_year = current_year
        
        # Use default semester from environment variable if not provided
        if current_semester is None:
            current_semester = os.environ.get('DEFAULT_SEMESTER', 'Fall')
        self.current_semester = current_semester
        
        # Calculate next semester for recommendations
        self.next_semester, self.next_year = self._get_next_semester(current_semester, current_year)
        
        # BSDS Schedule Template (hardcoded based on sample schedule)
        # Format: {semester_number: {slot: [course_ids]}}
        # Semester 1 = Fall 1, Semester 2 = Spring 1, etc.
        self.bsds_schedule = {
            1: {  # Fall 1 (Freshman)
                'main': [1, 6, 11],  # CS100, CS111, CS110
                'gened': [],  # Gen-Ed 1
                'foundation': [28]  # FND101
            },
            2: {  # Spring 1
                'main': [2, 7, 12, 16],  # CS101, BUS101, DS120, CS104
                'gened': [],
                'foundation': [29]  # FND102
            },
            3: {  # Fall 2
                'main': [3, 8, 13],  # CS102, CS107, DS115
                'gened': [],
                'foundation': [30]  # FND103
            },
            4: {  # Spring 2
                'main': [4, 9, 14, 17],  # ENGS211, CS108, DS205, DS150
                'gened': [],
                'foundation': [31]  # FND104
            },
            5: {  # Fall 3
                'main': [10, 15, 18],  # DS110, CS246, DS116
                'gened': [],
                'foundation': [32]  # FND221
            },
            6: {  # Spring 3
                'main': [19],  # CS251
                'gened': [],
                'foundation': [33]  # FND222
            },
            7: {  # Fall 4
                'main': [],  # Track courses + electives
                'gened': [],
                'foundation': []
            },
            8: {  # Spring 4
                'main': [5],  # DS299 Capstone
                'gened': [],
                'foundation': []
            }
        }
        
        # Gen-Ed cluster groups
        # Group A: GENED cluster_number 1,2,3 (cluster_id 7,8,9)
        # Group B: GENED cluster_number 4,5,6 (cluster_id 10,11,12)
        # Group C: We'll use BSDS clusters 7,8,9 (cluster_id 14,15,16) or interpret as additional Gen-Ed
        self.gened_groups = {
            'A': [7, 8, 9],   # GENED cluster_id with cluster_number 1,2,3
            'B': [10, 11, 12], # GENED cluster_id with cluster_number 4,5,6
            'C': [14, 15, 16]   # BSDS clusters (or additional requirement)
        }
        
        # Build helper mappings
        self._build_mappings()
    
    def _get_program_from_cluster_id(self, cluster_id):
        """
        Description:
            Derive program name from cluster_id based on data generator logic.
        
        Input:
            cluster_id (int): Cluster ID
        
        Output:
            str: Program name ('FND', 'GENED', 'BSDS') or None
        """
        # Based on university_data_generator.py:
        # Clusters 1-6: FND
        # Clusters 7-12: GENED
        # Clusters 13-16: BSDS
        if 1 <= cluster_id <= 6:
            return 'FND'
        elif 7 <= cluster_id <= 12:
            return 'GENED'
        elif 13 <= cluster_id <= 16:
            return 'BSDS'
        else:
            return None
    
    def _build_mappings(self):
        """
        Description:
            Build helper mappings for efficient lookups.
        
        Input:
            None (uses self.data)
        
        Output:
            None (modifies instance variables)
        """
        # Map course_id to clusters
        self.course_to_clusters = {}
        if 'course_cluster' in self.data and len(self.data['course_cluster']) > 0:
            for _, row in self.data['course_cluster'].iterrows():
                course_id = int(row['course_id'])
                cluster_id = int(row['cluster_id'])
                if course_id not in self.course_to_clusters:
                    self.course_to_clusters[course_id] = []
                self.course_to_clusters[course_id].append(cluster_id)
        
        # Map cluster_id to cluster info
        self.cluster_info = {}
        if 'clusters' in self.data and len(self.data['clusters']) > 0:
            for _, row in self.data['clusters'].iterrows():
                cluster_id = int(row['cluster_id'])
                self.cluster_info[cluster_id] = {
                    'cluster_number': int(row['cluster_number']),
                    'prog_name': self._get_program_from_cluster_id(cluster_id),
                    'description': row.get('theme', '')  # Use 'theme' instead of 'description'
                }
        
        # Map sections to time slots
        self.section_to_timeslot = {}
        if 'sections' in self.data and len(self.data['sections']) > 0:
            for _, row in self.data['sections'].iterrows():
                self.section_to_timeslot[int(row['id'])] = int(row.get('time_slot_id', 0))
        
        # Map time_slot_id to time info
        self.timeslot_info = {}
        if 'time_slots' in self.data and len(self.data['time_slots']) > 0:
            for _, row in self.data['time_slots'].iterrows():
                slot_id = int(row['time_slot_id'])
                self.timeslot_info[slot_id] = {
                    'day_of_week': row.get('day_of_week', ''),
                    'start_time': row.get('start_time', ''),
                    'end_time': row.get('end_time', ''),
                    'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else 0,
                    'semester': row.get('semester', '')
                }
    
    def _get_next_semester(self, current_semester, current_year):
        """
        Description:
        Calculate the next semester for recommendations.
        If current is Fall, next is Spring (same year)
        If current is Spring, next is Fall (next year)
        If current is Summer, next is Fall (same year)
        
        Input:
            current_semester (str): Current semester ('Fall', 'Spring', 'Summer')
            current_year (int): Current year
        
        Output:
            tuple: (next_semester, next_year)
        """
        if current_semester == 'Fall':
            return 'Spring', current_year
        elif current_semester == 'Spring':
            return 'Fall', current_year + 1
        elif current_semester == 'Summer':
            return 'Fall', current_year
        else:
            # Default: assume next is Spring
            return 'Spring', current_year
    
    def get_student_credits(self, student_id):
        """
        Description:
        Calculate total credits completed by student from takes table.
        This is the source of truth - credits are calculated from actual completed courses.
        
        Input:
            student_id (int): Student ID
        
        Output:
            int: Total credits completed
        """
        student_takes = self.data['takes'][
            (self.data['takes']['student_id'] == student_id) & 
            (self.data['takes']['status'] == 'completed')
        ]
        
        if len(student_takes) == 0:
            return 0
        
        # Get course IDs from sections
        section_ids = student_takes['section_id'].values
        completed_courses = self.data['sections'][
            self.data['sections']['id'].isin(section_ids)
        ]['course_id'].values
        
        # Sum credits
        total_credits = 0
        for course_id in completed_courses:
            course = self.data['courses'][self.data['courses']['id'] == course_id]
            if len(course) > 0:
                total_credits += int(course.iloc[0]['credits'])
        
        return total_credits
    
    def get_student_standing(self, student_id):
        """
        Description:
            Determine student standing based on credits.
        
        Input:
            student_id (int): Student ID
        
        Output:
            str: Student standing ('Freshman', 'Sophomore', 'Junior', 'Senior')
        """
        credits = self.get_student_credits(student_id)
        if credits < 30:
            return 'Freshman'
        elif credits < 60:
            return 'Sophomore'
        elif credits < 90:
            return 'Junior'
        else:
            return 'Senior'
    
    def get_student_completed_courses(self, student_id):
        """
        Description:
            Get set of completed course IDs for a student.
        
        Input:
            student_id (int): Student ID
        
        Output:
            set: Set of completed course IDs
        """
        student_takes = self.data['takes'][
            (self.data['takes']['student_id'] == student_id) & 
            (self.data['takes']['status'] == 'completed')
        ]
        
        if len(student_takes) == 0:
            return set()
        
        section_ids = student_takes['section_id'].values
        completed_courses = self.data['sections'][
            self.data['sections']['id'].isin(section_ids)
        ]['course_id'].unique()
        
        return set(completed_courses)
    
    def get_student_cluster_profile(self, student_id):
        """
        Description:
        Get student's cluster completion profile.
        
        Input:
            student_id (int): Student ID
        
        Output:
            dict: Dictionary mapping cluster_id to count of completed courses
        """
        completed_courses = self.get_student_completed_courses(student_id)
        cluster_counts = {}
        
        for course_id in completed_courses:
            clusters = self.course_to_clusters.get(int(course_id), [])
            for cluster_id in clusters:
                cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
        
        return cluster_counts
    
    def get_remaining_gened_requirements(self, student_id):
        """
        Description:
            Calculate remaining Gen-Ed requirements for a student.
        
        Input:
            student_id (int): Student ID
        
        Output:
            dict: Dictionary mapping group ('A', 'B', 'C') to remaining count needed
        """
        cluster_profile = self.get_student_cluster_profile(student_id)
        
        requirements = {
            'A': 3,  # Need 3 from clusters 7,8,9
            'B': 3,  # Need 3 from clusters 10,11,12
            'C': 3   # Need 3 from clusters 14,15,16 (or adjust based on requirements)
        }
        
        for group, cluster_ids in self.gened_groups.items():
            completed = sum(cluster_profile.get(cid, 0) for cid in cluster_ids)
            requirements[group] = max(0, requirements[group] - completed)
        
        return requirements
    
    def filter_by_time_preference(self, sections_df, time_preference='any'):
        """
        Description:
        Filter sections by time-of-day preference.
        
        Input:
            sections_df (DataFrame): DataFrame of sections to filter
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', or 'any')
        
        Output:
            DataFrame: Filtered sections DataFrame
        """
        if len(sections_df) == 0:
            return sections_df
        
        # If 'any', return all sections without filtering
        if time_preference == 'any' or time_preference is None:
            return sections_df
        
        filtered_sections = []
        
        for _, section in sections_df.iterrows():
            section_id = int(section['id'])
            timeslot_id = self.section_to_timeslot.get(section_id)
            
            if timeslot_id and timeslot_id in self.timeslot_info:
                time_info = self.timeslot_info[timeslot_id]
                start_time = time_info.get('start_time', '')
                
                if start_time:
                    try:
                        # Parse time (format: HH:MM:SS)
                        hour = int(start_time.split(':')[0])
                        
                        # Check time preference match
                        if time_preference == 'morning' and 8 <= hour < 12:
                            filtered_sections.append(section)
                        elif time_preference == 'afternoon' and 12 <= hour < 17:
                            filtered_sections.append(section)
                        elif time_preference == 'evening' and (17 <= hour or hour < 8):
                            filtered_sections.append(section)
                    except Exception:
                        # If parsing fails, include the section (assume it matches)
                        filtered_sections.append(section)
            else:
                # If no time info and time_preference is 'any', include the section
                # Otherwise, exclude sections without time info when filtering by specific time preference
                if time_preference == 'any':
                    filtered_sections.append(section)
        
        if filtered_sections:
            return pd.DataFrame(filtered_sections)
        return pd.DataFrame()
    
    def filter_courses_by_prereqs(self, course_ids, student_id):
        """
        Description:
            Filter courses to only those where prerequisites are satisfied.
        
        Input:
            course_ids (list): List of course IDs to filter
            student_id (int): Student ID
        
        Output:
            list: List of course IDs where all prerequisites are satisfied
        """
        completed = self.get_student_completed_courses(student_id)
        eligible = []
        
        for course_id in course_ids:
            # Get prerequisites
            prereqs = self.data['prerequisites'][
                self.data['prerequisites']['course_id'] == course_id
            ]['prerequisite_id'].values
            
            # Check if all prerequisites are completed
            if len(prereqs) == 0 or all(int(p) in completed for p in prereqs):
                eligible.append(course_id)
        
        return eligible
    
    def _filter_sections_with_fallbacks(self, sections, time_preference):
        """
        Description:
            Filter sections by semester and time preference with multiple fallback strategies.
            This is a helper method to reduce code duplication.
        
        Input:
            sections: DataFrame of sections to filter
            time_preference: Time preference ('morning', 'afternoon', 'evening', 'any')
        
        Output:
            DataFrame: Filtered sections DataFrame
        """
        if len(sections) == 0:
            return sections.copy()
        
        # Try strict filtering first (next semester + time preference)
        sections_filtered = self.filter_by_semester_availability(sections.copy())
        sections_filtered = self.filter_by_time_preference(sections_filtered, time_preference)
        
        # If no sections match both semester AND time preference, try just time preference
        if len(sections_filtered) == 0 and time_preference != 'any':
            sections_filtered = self.filter_by_time_preference(sections.copy(), time_preference)
        
        # Final fallback: if time_preference is 'any', try with just semester
        if len(sections_filtered) == 0 and time_preference == 'any':
            sections_filtered = self.filter_by_semester_availability(sections.copy())
        
        # Ultimate fallback: if still nothing and time_preference is 'any', use all sections
        if len(sections_filtered) == 0 and time_preference == 'any':
            sections_filtered = sections.copy()
        
        return sections_filtered
    
    def filter_by_semester_availability(self, sections_df, use_next_semester=True):
        """
        Description:
        Filter sections to only those available in next semester/year (for recommendations).
        
        Input:
            sections_df (DataFrame): DataFrame of sections to filter
            use_next_semester (bool): If True, filter by next semester; if False, use current semester
        
        Output:
            DataFrame: Filtered sections DataFrame
        """
        if len(sections_df) == 0:
            return sections_df
        
        available_sections = []
        target_year = self.next_year if use_next_semester else self.current_year
        target_semester = self.next_semester if use_next_semester else self.current_semester
        
        for _, section in sections_df.iterrows():
            section_id = int(section['id'])
            timeslot_id = self.section_to_timeslot.get(section_id)
            
            if timeslot_id and timeslot_id in self.timeslot_info:
                time_info = self.timeslot_info[timeslot_id]
                year = time_info.get('year', 0)
                semester = time_info.get('semester', '')
                
                # Priority 1: Exact match for next semester
                if year == target_year and semester == target_semester:
                    available_sections.append(section)
                # Priority 2: Same semester in future years
                elif year > target_year and semester == target_semester:
                    available_sections.append(section)
                # Priority 3: Any future semester/year as fallback
                elif year >= target_year:
                    available_sections.append(section)
            else:
                # If no time info, include it (assume available)
                available_sections.append(section)
        
        if available_sections:
            return pd.DataFrame(available_sections)
        return pd.DataFrame()
    
    def get_schedule_template_for_semester(self, student_id):
        """
        Description:
        Determine which semester template to use based on student's progress.
        
        Input:
            student_id (int): Student ID
        
        Output:
            int: Semester number (1-8) corresponding to BSDS schedule template
        """
        credits = self.get_student_credits(student_id)
        
        # Map credits to semester
        if credits < 15:
            return 1  # Fall 1
        elif credits < 30:
            return 2  # Spring 1
        elif credits < 45:
            return 3  # Fall 2
        elif credits < 60:
            return 4  # Spring 2
        elif credits < 75:
            return 5  # Fall 3
        elif credits < 90:
            return 6  # Spring 3
        elif credits < 105:
            return 7  # Fall 4
        else:
            return 8  # Spring 4
    
    def recommend_gened(self, student_id, time_preference='any'):
        """
        Description:
        Recommend a Gen-Ed course based on remaining requirements.
        
        Input:
            student_id (int): Student ID
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
        
        Output:
            dict: Course recommendation dictionary or None if all requirements met
        """
        remaining = self.get_remaining_gened_requirements(student_id)
        
        # Find which group needs courses
        target_group = None
        for group, needed in remaining.items():
            if needed > 0:
                target_group = group
                break
        
        if target_group is None:
            return None  # All Gen-Ed requirements met
        
        # Get cluster IDs for this group
        target_clusters = self.gened_groups[target_group]
        
        # Find courses in these clusters
        candidate_courses = []
        if 'course_cluster' in self.data and len(self.data['course_cluster']) > 0:
            for _, row in self.data['course_cluster'].iterrows():
                cluster_id = int(row['cluster_id'])
                if cluster_id in target_clusters:
                    course_id = int(row['course_id'])
                    candidate_courses.append(course_id)
        
        # Filter by prerequisites
        candidate_courses = self.filter_courses_by_prereqs(candidate_courses, student_id)
        
        # Remove already completed/enrolled
        completed = self.get_student_completed_courses(student_id)
        enrolled = self._get_enrolled_courses(student_id)
        candidate_courses = [c for c in candidate_courses if c not in completed and c not in enrolled]
        
        # Fallback: if no courses found in specific clusters, try to find any Gen-Ed course
        # (courses in GENED program that aren't completed)
        if not candidate_courses:
            # Get all courses in GENED program
            if 'hascourse' in self.data and len(self.data['hascourse']) > 0:
                gened_courses = self.data['hascourse'][
                    self.data['hascourse']['prog_name'] == 'GENED'
                ]['courseid'].unique()
                
                # Filter by prerequisites and remove completed/enrolled
                gened_courses = self.filter_courses_by_prereqs(gened_courses.tolist(), student_id)
                gened_courses = [c for c in gened_courses if c not in completed and c not in enrolled]
                candidate_courses = gened_courses
        
        if not candidate_courses:
            return None
        
        # Get sections for candidate courses
        sections = self.data['sections'][
            self.data['sections']['course_id'].isin(candidate_courses)
        ]
        
        if len(sections) == 0:
            return None
        
        # Filter sections with fallback strategies
        sections_filtered = self._filter_sections_with_fallbacks(sections, time_preference)
        
        if len(sections_filtered) == 0:
            return None
        
        # Pick first available section
        section = sections_filtered.iloc[0]
        course_id = int(section['course_id'])
        course = self.data['courses'][self.data['courses']['id'] == course_id].iloc[0]
        
        return {
            'course_id': course_id,
            'course_name': course['name'],
            'cluster': self._get_cluster_names(course_id, default='Gen-Ed'),
            'credits': int(course['credits']),
            'section_id': int(section['id']),
            'time_slot': self._get_time_slot_string(int(section['id'])),
            'why_recommended': [f'Gen-Ed requirement for cluster group {target_group}']
        }
    
    def recommend_main_courses(self, student_id, time_preference='any', n=3):
        """
        Description:
        Recommend main courses (Core/Track) based on BSDS schedule.
        
        Input:
            student_id (int): Student ID
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
            n (int): Number of courses to recommend (default: 3)
        
        Output:
            list: List of course recommendation dictionaries
        """
        semester_num = self.get_schedule_template_for_semester(student_id)
        template = self.bsds_schedule.get(semester_num, {})
        template_courses = template.get('main', [])
        
        # Filter by prerequisites
        eligible_courses = self.filter_courses_by_prereqs(template_courses, student_id)
        
        # Remove completed/enrolled
        completed = self.get_student_completed_courses(student_id)
        enrolled = self._get_enrolled_courses(student_id)
        eligible_courses = [c for c in eligible_courses if c not in completed and c not in enrolled]
        
        recommendations = []
        
        # Try to get up to n courses from template
        for course_id in eligible_courses[:n]:
            rec = self._try_recommend_course(course_id, time_preference, 
                                            f'Required for semester {semester_num} per BSDS schedule')
            if rec:
                recommendations.append(rec)
        
        # If we don't have enough recommendations, find alternative courses
        if len(recommendations) < n:
            # Get all BSDS program courses that student hasn't taken
            if 'hascourse' in self.data and len(self.data['hascourse']) > 0:
                bsds_courses = self.data['hascourse'][
                    self.data['hascourse']['prog_name'] == 'BSDS'
                ]['courseid'].unique().tolist()
                
                # Filter by prerequisites and remove completed/enrolled
                bsds_courses = self.filter_courses_by_prereqs(bsds_courses, student_id)
                bsds_courses = [c for c in bsds_courses if c not in completed and c not in enrolled]
                
                # Remove courses already recommended
                recommended_ids = [r['course_id'] for r in recommendations]
                bsds_courses = [c for c in bsds_courses if c not in recommended_ids and c not in template_courses]
                
                # Try to fill remaining slots
                for course_id in bsds_courses[:n - len(recommendations)]:
                    rec = self._try_recommend_course(course_id, time_preference, 
                                                    'Alternative BSDS course based on prerequisites')
                    if rec:
                        recommendations.append(rec)
                        if len(recommendations) >= n:
                            break
        
        return recommendations
    
    def _try_recommend_course(self, course_id, time_preference, why_recommended):
        """
        Description:
        Helper method to try recommending a course with proper filtering.
        
        Input:
            course_id (int): Course ID to recommend
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
            why_recommended (str): Reason for recommendation
        
        Output:
            dict: Recommendation dictionary or None if no valid section found
        """
        # Get sections
        sections = self.data['sections'][
            self.data['sections']['course_id'] == course_id
        ]
        
        if len(sections) == 0:
            return None
        
        # Filter sections with fallback strategies
        sections_filtered = self._filter_sections_with_fallbacks(sections, time_preference)
        
        if len(sections_filtered) == 0:
            return None
        
        section = sections_filtered.iloc[0]
        course = self.data['courses'][self.data['courses']['id'] == course_id].iloc[0]
        
        return {
            'course_id': course_id,
            'course_name': course['name'],
            'cluster': self._get_cluster_names(course_id, default='Core'),
            'credits': int(course['credits']),
            'section_id': int(section['id']),
            'time_slot': self._get_time_slot_string(int(section['id'])),
            'why_recommended': [why_recommended]
        }
    
    def recommend_foundation(self, student_id, time_preference='any'):
        """
        Description:
            Recommend a Foundation course if needed based on BSDS schedule template.
        
        Input:
            student_id (int): Student ID
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
        
        Output:
            dict: Foundation course recommendation dictionary or None
        """
        semester_num = self.get_schedule_template_for_semester(student_id)
        template = self.bsds_schedule.get(semester_num, {})
        foundation_courses = template.get('foundation', [])
        
        if not foundation_courses:
            return None
        
        # Check if student has completed/enrolled foundation requirements
        completed = self.get_student_completed_courses(student_id)
        enrolled = self._get_enrolled_courses(student_id)
        
        # Filter by prerequisites and availability
        eligible = self.filter_courses_by_prereqs(foundation_courses, student_id)
        eligible = [c for c in eligible if c not in completed and c not in enrolled]
        
        if not eligible:
            return None
        
        # Get sections
        sections = self.data['sections'][
            self.data['sections']['course_id'].isin(eligible)
        ]
        
        if len(sections) == 0:
            return None
        
        # Filter sections with fallback strategies
        sections_filtered = self._filter_sections_with_fallbacks(sections, time_preference)
        
        if len(sections_filtered) == 0:
            return None
        
        section = sections_filtered.iloc[0]
        course_id = int(section['course_id'])
        course = self.data['courses'][self.data['courses']['id'] == course_id].iloc[0]
        
        return {
            'course_id': course_id,
            'course_name': course['name'],
            'cluster': 'Foundation',
            'credits': int(course['credits']),
            'section_id': int(section['id']),
            'time_slot': self._get_time_slot_string(int(section['id'])),
            'why_recommended': ['Foundation requirement']
        }
    
    def _get_enrolled_courses(self, student_id):
        """
        Description:
            Get set of currently enrolled course IDs for a student.
        
        Input:
            student_id (int): Student ID
        
        Output:
            set: Set of currently enrolled course IDs
        """
        student_takes = self.data['takes'][
            (self.data['takes']['student_id'] == student_id) & 
            (self.data['takes']['status'] == 'enrolled')
        ]
        
        if len(student_takes) == 0:
            return set()
        
        section_ids = student_takes['section_id'].values
        enrolled_courses = self.data['sections'][
            self.data['sections']['id'].isin(section_ids)
        ]['course_id'].unique()
        
        return set(enrolled_courses)
    
    def _get_cluster_names(self, course_id, default='Core'):
        """
        Description:
            Get cluster names for a course as a comma-separated string.
        
        Input:
            course_id (int): Course ID
            default (str): Default cluster name if no clusters found
        
        Output:
            str: Comma-separated cluster names or default
        """
        clusters = self.course_to_clusters.get(course_id, [])
        cluster_names = []
        for cid in clusters:
            if cid in self.cluster_info:
                cluster_names.append(self.cluster_info[cid]['description'])
        return ', '.join(cluster_names) if cluster_names else default
    
    def _get_time_slot_string(self, section_id):
        """
        Description:
            Get human-readable time slot string for a section.
        
        Input:
            section_id (int): Section ID
        
        Output:
            str: Human-readable time slot string (e.g., "Monday 09:00:00-10:30:00") or "TBA"
        """
        timeslot_id = self.section_to_timeslot.get(section_id)
        if timeslot_id and timeslot_id in self.timeslot_info:
            info = self.timeslot_info[timeslot_id]
            day = info.get('day_of_week', '')
            start = info.get('start_time', '')
            end = info.get('end_time', '')
            if start and end:
                return f"{day} {start}-{end}"
        return "TBA"
    
    def recommend_semester(self, student_id, time_preference='any'):
        """
        Description:
            Recommend a full semester schedule (5 courses) for a student.
            Combines main courses, Gen-Ed, and foundation courses.
        
        Input:
            student_id (int): Student ID to generate recommendations for
            time_preference (str): Time preference ('morning', 'afternoon', 'evening', 'any')
        
        Output:
            list: List of recommendation dictionaries, up to 5 courses
        """
        recommendations = []
        
        # Slot 1-3: Main courses (Core/Track)
        main_courses = self.recommend_main_courses(student_id, time_preference, n=3)
        recommendations.extend(main_courses)
        
        # Slot 4: Gen-Ed
        gened = self.recommend_gened(student_id, time_preference)
        if gened:
            recommendations.append(gened)
        
        # Slot 5: Foundation or Free Elective
        foundation = self.recommend_foundation(student_id, time_preference)
        if foundation:
            recommendations.append(foundation)
        
        return recommendations