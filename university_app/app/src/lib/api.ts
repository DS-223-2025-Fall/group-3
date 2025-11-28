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

export interface UIElementPosition {
  student_id: number
  test_group: string
  ui_config: {
    search_bar: string
    dropdowns: string
    buttons: string
    header_color: string
    search_button_position: string
  }
  assigned_at: string
}

export interface UIElementClick {
  student_id: number
  element_type: string
  element_id?: string
  element_position?: string
  page_url?: string
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

export async function getUIPositions(studentId: number): Promise<UIElementPosition> {
  try {
    const response = await fetch(`${API_BASE_URL}/ui/positions/${studentId}`)
    if (!response.ok) {
      throw new Error('Failed to fetch UI positions')
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching UI positions:', error)
    // Return default configuration
    return {
      student_id: studentId,
      test_group: 'A',
      ui_config: {
        search_bar: 'top',
        dropdowns: 'left',
        buttons: 'right',
        header_color: '#1e3a5f',
        search_button_position: 'inline'
      },
      assigned_at: new Date().toISOString()
    }
  }
}

export async function trackUIClick(click: UIElementClick): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/ui/clicks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(click),
    })
    if (!response.ok) {
      throw new Error('Failed to track click')
    }
  } catch (error) {
    console.error('Error tracking click:', error)
    // Don't throw - we don't want click tracking to break the app
  }
}

