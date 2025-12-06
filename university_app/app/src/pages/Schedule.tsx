import { useState, useEffect } from 'react'
import { Calendar, Sparkles, FileText } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/contexts/AuthContext'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Course, fetchCourses, fetchDraftSchedules, DraftSchedule, deleteDraftSchedule } from '@/lib/api'
import DraftScheduleModal from '@/components/DraftSchedule'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8008'

interface RecommendationResult {
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

export default function Schedule() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<'recommended' | 'draft'>('recommended')
  const [recommendations, setRecommendations] = useState<RecommendationResult[]>([])
  const [recommendedCourses, setRecommendedCourses] = useState<Course[]>([])
  const [draftSchedules, setDraftSchedules] = useState<DraftSchedule[]>([])
  const [isDraftModalOpen, setIsDraftModalOpen] = useState(false)
  const [selectedDraftCourses, setSelectedDraftCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [draftLoading, setDraftLoading] = useState(false)

  // Load recommended schedule
  useEffect(() => {
    if (user?.student_id && activeTab === 'recommended') {
      loadRecommendedSchedule()
    }
  }, [user?.student_id, activeTab])

  // Load draft schedules
  useEffect(() => {
    if (activeTab === 'draft') {
      loadDraftSchedules()
    }
  }, [activeTab])

  const loadRecommendedSchedule = async () => {
    if (!user?.student_id) {
      console.log('No student_id found for user:', user)
      return
    }
    
    setLoading(true)
    try {
      const url = `${API_BASE_URL}/recommendation-results?student_id=${user.student_id}`
      console.log('Fetching recommendations from:', url)
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Failed to fetch recommendations')
      }
      const data: RecommendationResult[] = await response.json()
      console.log('Received recommendations:', data.length, 'records for student_id:', user.student_id)
      setRecommendations(data)

      // Convert recommendations to Course format for display
      if (data.length > 0) {
        // Map recommended_section_id (integer) to section IDs
        const sectionIds = data.map(r => r.recommended_section_id)
        console.log('Looking for sections:', sectionIds)
        const courses = await fetchCourses({})
        console.log('Total courses available:', courses.length)
        // Match courses where the section id (c.id is section.id as string) matches recommended_section_id
        const recommendedCourseList = courses.filter(c => 
          sectionIds.includes(parseInt(c.id))
        )
        console.log('Matched courses:', recommendedCourseList.length)
        if (recommendedCourseList.length === 0 && sectionIds.length > 0) {
          console.warn('No courses matched for section IDs:', sectionIds)
          console.log('Available course IDs (first 10):', courses.slice(0, 10).map(c => c.id))
        }
        setRecommendedCourses(recommendedCourseList)
      } else {
        console.log('No recommendations found in API response')
        setRecommendedCourses([])
      }
    } catch (error) {
      console.error('Error loading recommended schedule:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDraftSchedules = async () => {
    if (!user?.student_id) {
      console.log('No student_id found for user:', user)
      return
    }
    
    setDraftLoading(true)
    try {
      const schedules = await fetchDraftSchedules(user.student_id)
      setDraftSchedules(schedules)
    } catch (error) {
      console.error('Error loading draft schedules:', error)
    } finally {
      setDraftLoading(false)
    }
  }

  const handleOpenDraft = async (schedule: DraftSchedule) => {
    // Fetch all courses and filter by section IDs
    try {
      const allCourses = await fetchCourses({})
      const scheduleCourses = allCourses.filter(course => 
        schedule.section_ids.includes(parseInt(course.id))
      )
      setSelectedDraftCourses(scheduleCourses)
      setIsDraftModalOpen(true)
    } catch (error) {
      console.error('Error loading draft schedule courses:', error)
      toast.error('Failed to load schedule courses')
    }
  }

  const handleDeleteDraft = async (scheduleId: number) => {
    if (!confirm('Are you sure you want to delete this schedule?')) {
      return
    }
    
    try {
      await deleteDraftSchedule(scheduleId)
      toast.success('Schedule deleted successfully')
      loadDraftSchedules() // Reload the list
    } catch (error) {
      console.error('Error deleting schedule:', error)
      toast.error('Failed to delete schedule')
    }
  }

  const parseCourseTime = (timeRange?: string) => {
    if (!timeRange) return Number.POSITIVE_INFINITY
    const [start] = timeRange.split('-')
    if (!start) return Number.POSITIVE_INFINITY
    const [hours = '0', minutes = '0'] = start.trim().split(':')
    const hourValue = parseInt(hours, 10)
    const minuteValue = parseInt(minutes, 10)
    if (Number.isNaN(hourValue) || Number.isNaN(minuteValue)) {
      return Number.POSITIVE_INFINITY
    }
    return hourValue * 60 + minuteValue
  }

  const isMWFCourse = (days?: string): boolean => {
    if (!days) return false
    const normalizedDays = days.toLowerCase()
    return (
      normalizedDays.includes('monday') ||
      normalizedDays.includes('wednesday') ||
      normalizedDays.includes('friday')
    )
  }

  const isTThCourse = (days?: string): boolean => {
    if (!days) return false
    const normalizedDays = days.toLowerCase()
    return (
      normalizedDays.includes('tuesday') ||
      normalizedDays.includes('thursday')
    )
  }

  const renderCourseCard = (course: Course) => (
    <div
      key={course.id}
      className="border rounded-lg p-4 bg-white hover:bg-gray-50 transition"
    >
      <div className="flex-1">
        <h3 className="font-semibold text-lg">
          <span className="font-bold">{course.name}</span>
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Section {course.section} •{' '}
          {course.instructorBioUrl ? (
            <a
              href={course.instructorBioUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#1e3a5f] hover:text-[#2a4f7a] underline-offset-2"
            >
              {course.instructor}
            </a>
          ) : (
            <span>{course.instructor}</span>
          )}
        </p>
        <p className="text-sm text-gray-600">
          {course.time}
        </p>
        <p className="text-sm text-gray-600">
          {course.location} • {course.duration} • {course.credits || 0} Credits
        </p>
        {course.cluster && course.cluster.length > 0 && (
          <div className="flex gap-2 mt-2">
            {course.cluster.map((clusterNum) => (
              <span
                key={clusterNum}
                className="px-2 py-1 bg-yellow-400 text-[#1e3a5f] rounded-full text-xs font-semibold"
              >
                Cluster {clusterNum}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-4xl font-bold text-[#1e3a5f]">Schedule</h1>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'recommended' | 'draft')} className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="recommended" className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Recommended Schedule
          </TabsTrigger>
          <TabsTrigger value="draft" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Draft Schedule
          </TabsTrigger>
        </TabsList>

        <TabsContent value="recommended" className="mt-6">
          <div className="bg-white rounded-lg shadow-md p-8">
            {loading ? (
              <p className="text-center text-gray-500 py-8">Loading recommended schedule...</p>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-8">
                <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">No recommended schedule available</p>
                <p className="text-sm text-gray-500">
                  Recommendations will appear here once generated by the recommendation system.
                </p>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-semibold text-[#1e3a5f] mb-2">
                    Your Recommended Schedule
                  </h2>
                  <p className="text-gray-600">
                    Based on your academic progress and preferences
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Monday / Wednesday / Friday Section */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
                      <Calendar className="h-5 w-5 text-[#1e3a5f]" />
                      <h3 className="text-lg font-semibold text-[#1e3a5f]">
                        Monday / Wednesday / Friday
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {recommendedCourses
                        .filter((course) => isMWFCourse(course.days))
                        .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))
                        .map(renderCourseCard)}
                    </div>
                  </div>

                  {/* Tuesday / Thursday Section */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
                      <Calendar className="h-5 w-5 text-[#1e3a5f]" />
                      <h3 className="text-lg font-semibold text-[#1e3a5f]">
                        Tuesday / Thursday
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {recommendedCourses
                        .filter((course) => isTThCourse(course.days))
                        .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))
                        .map(renderCourseCard)}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="draft" className="mt-6">
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-[#1e3a5f] mb-2">
                Draft Schedules
              </h2>
              <p className="text-gray-600">
                Manage your draft schedules created from the Classes page
              </p>
            </div>

            {draftLoading ? (
              <div className="text-center py-8">
                <p className="text-gray-500">Loading draft schedules...</p>
              </div>
            ) : draftSchedules.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">No draft schedules yet</p>
                <p className="text-sm text-gray-500">
                  Go to the Classes page, select courses, and click "Draft Schedule" to create your first draft.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {draftSchedules.map((schedule) => (
                  <div
                    key={schedule.draft_schedule_id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div
                        className="flex-1 cursor-pointer"
                        onClick={() => handleOpenDraft(schedule)}
                      >
                        <h3 className="font-semibold text-lg text-[#1e3a5f]">
                          {schedule.name}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {schedule.section_ids.length} course(s) • Created {new Date(schedule.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleOpenDraft(schedule)}
                          className="p-2 hover:bg-gray-100 rounded"
                          title="View schedule"
                        >
                          <Calendar className="h-5 w-5 text-[#1e3a5f]" />
                        </button>
                        <button
                          onClick={() => handleDeleteDraft(schedule.draft_schedule_id)}
                          className="p-2 hover:bg-red-50 rounded text-red-600"
                          title="Delete schedule"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      <DraftScheduleModal
        open={isDraftModalOpen}
        onOpenChange={setIsDraftModalOpen}
        selectedCourses={selectedDraftCourses}
        onRemoveCourse={() => {}}
        onScheduleSaved={() => {
          loadDraftSchedules()
        }}
      />
    </div>
  )
}

