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
    // Return mock data as fallback
    return []
  }
}

