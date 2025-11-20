import { Course } from '@/lib/api'

export const mockCourses: Course[] = [
  {
    id: '1',
    code: 'CHSS113',
    name: 'Critical Thinking and Writing',
    cluster: [3, 4, 6],
    section: 'A',
    instructor: 'Dr. Anna Martirosyan',
    days: 'Monday, Wednesday, Friday',
    time: '12:30-13:20',
    takenSeats: 26,
    totalSeats: 40,
    location: 'Main Building – Room 314M',
    duration: '14 weeks',
    syllabusUrl: '/syllabi/course_1_section_1.pdf'
  },
  {
    id: '2',
    code: 'ECON101',
    name: 'Principles of Microeconomics',
    cluster: [5, 8],
    section: 'C',
    instructor: 'Dr. Narine Hovhannisyan',
    days: 'Tuesday, Thursday',
    time: '11:00-12:30',
    takenSeats: 32,
    totalSeats: 40,
    location: 'Business Building – Room 220B',
    duration: '14 weeks',
    syllabusUrl: '/syllabi/course_2_section_1.pdf'
  },
  {
    id: '3',
    code: 'CS110',
    name: 'Intro to Computer Science',
    cluster: [1, 2],
    section: 'A',
    instructor: 'Dr. Vardges Melkonian',
    days: 'Monday, Wednesday, Friday',
    time: '10:00-11:00',
    takenSeats: 35,
    totalSeats: 40,
    location: 'Main Building – Room 201',
    duration: '14 weeks',
    syllabusUrl: '/syllabi/course_3_section_1.pdf'
  },
  {
    id: '4',
    code: 'DS120',
    name: 'Programming for Data Science',
    cluster: [1, 2, 5],
    section: 'B',
    instructor: 'Dr. Tigran Harutyunyan',
    days: 'Tuesday, Thursday',
    time: '14:00-15:30',
    takenSeats: 28,
    totalSeats: 40,
    location: 'Main Building – Room 305',
    duration: '14 weeks',
    syllabusUrl: '/syllabi/course_4_section_1.pdf'
  },
  {
    id: '5',
    code: 'CS100',
    name: 'Calculus 1',
    cluster: [1],
    section: 'A',
    instructor: 'Dr. Armen Petrosyan',
    days: 'Monday, Wednesday, Friday',
    time: '09:00-10:00',
    takenSeats: 40,
    totalSeats: 40,
    location: 'Main Building – Room 101',
    duration: '14 weeks',
    syllabusUrl: '/syllabi/course_5_section_1.pdf'
  }
]

