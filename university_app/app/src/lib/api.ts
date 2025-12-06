const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8008'

export interface Course {
  id: string
  code: string
  name: string
  cluster: number[]
  section: string
  instructor: string
  days: string
  time: string
  takenSeats: number
  totalSeats: number
  location: string
  duration: string
  syllabusUrl?: string
  instructorBioUrl?: string
  credits: number
  semester?: string
  year?: number
  semesterYear?: string
}

export interface Prerequisite {
  course_id: number
  prerequisite_id: number
}

export async function fetchCourses(params?: {
  year?: string
  semester?: string
  courseType?: string
  search?: string
}): Promise<Course[]> {
  try {
    const queryParams = new URLSearchParams()
    if (params?.year) queryParams.append('year', params.year)
    if (params?.semester) queryParams.append('semester', params.semester)
    if (params?.courseType) queryParams.append('course_type', params.courseType)
    if (params?.search) queryParams.append('search', params.search)

    const response = await fetch(`${API_BASE_URL}/sections?${queryParams}`)
    if (!response.ok) {
      throw new Error('Failed to fetch courses')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching courses:', error)
    // Return empty array - no mock data fallback, use real DB only
    return []
  }
}

export async function fetchPrerequisites(courseId: number): Promise<Prerequisite[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/prerequisites?course_id=${courseId}`)
    if (!response.ok) {
      throw new Error('Failed to fetch prerequisites')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching prerequisites:', error)
    return []
  }
}

export interface Program {
  prog_name: string
  dept_name?: string
}

export async function fetchPrograms(): Promise<Program[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/programs`)
    if (!response.ok) {
      throw new Error('Failed to fetch programs')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching programs:', error)
    return []
  }
}

export interface DraftSchedule {
  draft_schedule_id: number
  student_id: number
  name: string
  created_at: string
  updated_at?: string
  section_ids: number[]
}

export interface DraftScheduleCreate {
  student_id: number
  name: string
  section_ids: number[]
}

export async function fetchDraftSchedules(studentId?: number): Promise<DraftSchedule[]> {
  try {
    const url = studentId 
      ? `${API_BASE_URL}/draft-schedules?student_id=${studentId}`
      : `${API_BASE_URL}/draft-schedules`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('Failed to fetch draft schedules')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching draft schedules:', error)
    return []
  }
}

export async function createDraftSchedule(schedule: DraftScheduleCreate): Promise<DraftSchedule> {
  try {
    const response = await fetch(`${API_BASE_URL}/draft-schedules/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(schedule),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create draft schedule')
    }
    return await response.json()
  } catch (error) {
    console.error('Error creating draft schedule:', error)
    throw error
  }
}

export async function deleteDraftSchedule(draftScheduleId: number): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/draft-schedules/${draftScheduleId}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error('Failed to delete draft schedule')
    }
  } catch (error) {
    console.error('Error deleting draft schedule:', error)
    throw error
  }
}

