export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8008'

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

export interface GPAProgressPoint {
  term: string
  year: number
  semester: string
  gpa: number
}

export interface CreditsProgress {
  credit_earned: number
  total_credits: number
  remaining: number
}

export interface SemesterProgress {
  percentage: number
  days_passed: number
  days_total: number
}

export interface CourseCompletionByProgram {
  program: string
  taken: number
  remaining: number
  total: number
}

export interface GradeDistribution {
  grade: string
  count: number
  percentage: number
}

export interface PerformanceByCourseType {
  course_type: string
  average_gpa: number
  course_count: number
}

export interface CreditAccumulation {
  term: string
  year: number
  semester: string
  credits_earned: number
  cumulative_credits: number
}

export interface TimeSlotPerformance {
  time_slot: string
  average_gpa: number
  course_count: number
}

export interface CourseLoad {
  term: string
  year: number
  semester: string
  credits: number
}

export interface GradeTrendByCourseType {
  term: string
  year: number
  semester: string
  course_type: string
  gpa: number
}

export interface PrerequisiteStatus {
  course_id: number
  course_name: string
  prerequisites_completed: number
  prerequisites_total: number
  completion_percentage: number
}

export interface CourseDifficultyPerformance {
  course_id: number
  course_name: string
  credits: number
  grade: string
  gpa_value: number
}

export interface SemesterPerformanceHeatmap {
  day_of_week: string
  time_slot: string
  average_gpa: number
  course_count: number
}

export interface Statistics {
  gpa_progress: GPAProgressPoint[]
  credits_progress: CreditsProgress
  semester_progress: SemesterProgress
  course_completion: CourseCompletionByProgram[]
  grade_distribution: GradeDistribution[]
  performance_by_course_type: PerformanceByCourseType[]
  credit_accumulation: CreditAccumulation[]
  time_slot_performance: TimeSlotPerformance[]
  course_load: CourseLoad[]
  grade_trends_by_course_type: GradeTrendByCourseType[]
  prerequisites_status: PrerequisiteStatus[]
  course_difficulty_performance: CourseDifficultyPerformance[]
  semester_performance_heatmap: SemesterPerformanceHeatmap[]
}

export async function fetchStatistics(studentId: number): Promise<Statistics> {
  try {
    const response = await fetch(`${API_BASE_URL}/statistics/${studentId}`)
    if (!response.ok) {
      throw new Error('Failed to fetch statistics')
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching statistics:', error)
    throw error
  }
}

export interface GenerateRecommendationsParams {
  student_id: number
  time_preference: string
  semester?: string
  year?: number
}

export interface RecommendationResult {
  id: number
  student_id: number
  course_id: number | null
  recommended_section_id: number
  course_name: string | null
  cluster: string | null
  credits: number | null
  time_slot: string | null
  recommendation_score: string | null
  why_recommended: string | null
  slot_number: number | null
  model_version: string | null
  time_preference: string | null
  semester: string | null
  year: number | null
  created_at: string
}

export async function fetchRecommendationResults(studentId: number): Promise<RecommendationResult[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/recommendation-results?student_id=${studentId}`)
    if (!response.ok) {
      throw new Error('Failed to fetch recommendations')
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching recommendation results:', error)
    throw error
  }
}

export interface GenerateRecommendationsResponse {
  message: string
  count: number
}

export async function generateRecommendations(params: GenerateRecommendationsParams): Promise<GenerateRecommendationsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/recommendations/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate recommendations')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error generating recommendations:', error)
    throw error
  }
}

