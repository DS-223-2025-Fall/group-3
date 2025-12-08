import { useState, useEffect } from 'react'
import { Calendar, Sparkles, FileText, Clock, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/contexts/AuthContext'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Course, fetchCourses, fetchDraftSchedules, DraftSchedule, deleteDraftSchedule, generateRecommendations, fetchRecommendationResults, RecommendationResult } from '@/lib/api'
import DraftScheduleModal from '@/components/DraftSchedule'
import { groupCoursesByDays, getTimeCategory } from '@/lib/utils'
import CourseCard from '@/components/CourseCard'

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
  const [timePreference, setTimePreference] = useState<string>('any')
  const [generating, setGenerating] = useState(false)

  // Load recommended schedule
  useEffect(() => {
    if (user?.student_id && activeTab === 'recommended') {
      loadRecommendedSchedule()
    }
  }, [user?.student_id, activeTab, timePreference])

  // Load draft schedules
  useEffect(() => {
    if (activeTab === 'draft') {
      loadDraftSchedules()
    }
  }, [activeTab])

  const loadRecommendedSchedule = async () => {
    if (!user?.student_id) {
      return
    }
    
    setLoading(true)
    try {
      const data = await fetchRecommendationResults(user.student_id)
      
      // Fetch all courses first to get time information
      const courses = await fetchCourses({})
      
      // Create a map of section ID to course for quick lookup
      const sectionToCourse = new Map(
        courses.map(c => [parseInt(c.id), c])
      )
      
      // Filter by time preference based on actual course time, not stored preference
      let filtered = data
      if (timePreference !== 'any') {
        filtered = data.filter(r => {
          const course = sectionToCourse.get(r.recommended_section_id)
          if (!course) {
            // Course not found - might be from a different semester/year
            // Log for debugging but don't show to user
            console.debug(`Course not found for section ID: ${r.recommended_section_id}, recommendation ID: ${r.id}`)
            return false
          }
          if (!course.time) {
            // If no time info, exclude when filtering by specific time
            console.debug(`Course ${course.name} (section ${r.recommended_section_id}) has no time info`)
            return false
          }
          const timeCategory = getTimeCategory(course.time)
          if (timeCategory === 'unknown') {
            console.debug(`Could not categorize time "${course.time}" for course ${course.name}`)
            return false
          }
          return timeCategory === timePreference
        })
        
        // Debug: Log filtering results
        console.log(`Filtered ${filtered.length} of ${data.length} recommendations for ${timePreference} time preference`)
        if (filtered.length === 0 && data.length > 0) {
          console.log('Sample recommendations that were filtered out:', data.slice(0, 3).map(r => ({
            id: r.id,
            section_id: r.recommended_section_id,
            course_name: r.course_name,
            time_preference: r.time_preference
          })))
          console.log('Available courses in map:', Array.from(sectionToCourse.keys()).slice(0, 10))
        }
      }
      
      setRecommendations(filtered)

      // Convert recommendations to Course format for display
      if (filtered.length > 0) {
        const sectionIds = filtered.map(r => r.recommended_section_id)
        const recommendedCourseList = courses.filter(c => 
          sectionIds.includes(parseInt(c.id))
        )
        setRecommendedCourses(recommendedCourseList)
      } else {
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

  const handleGenerateRecommendations = async () => {
    if (!user?.student_id) {
      toast.error('Student ID not found')
      return
    }
    
    setGenerating(true)
    try {
      const result = await generateRecommendations({
        student_id: user.student_id,
        time_preference: timePreference,
        semester: 'Fall',
        year: 2025
      })
      
      toast.success(result.message || `Generated ${result.count} recommendations`)
      
      // Reload recommendations
      await loadRecommendedSchedule()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to generate recommendations')
    } finally {
      setGenerating(false)
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

  const { mwfCourses: recommendedMWF, tthCourses: recommendedTTh } = groupCoursesByDays(recommendedCourses)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-4xl font-bold text-[#1e3a5f]">Schedule</h1>
      </div>

      <Tabs 
        value={activeTab} 
        onValueChange={(v) => setActiveTab(v as 'recommended' | 'draft')} 
        className="w-full"
      >
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
            <div className="mb-6 flex items-center justify-between border-b border-gray-200 pb-4">
              <div>
                <h2 className="text-2xl font-semibold text-[#1e3a5f] mb-2">
                  Your Recommended Schedule
                </h2>
                <p className="text-gray-600">
                  Generate personalized course recommendations based on your preferences
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-[#1e3a5f]" />
                  <Select value={timePreference} onValueChange={setTimePreference}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Time Preference" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any Time</SelectItem>
                      <SelectItem value="morning">Morning</SelectItem>
                      <SelectItem value="afternoon">Afternoon</SelectItem>
                      <SelectItem value="evening">Evening</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={handleGenerateRecommendations}
                  disabled={generating || !user?.student_id}
                  className="bg-[#1e3a5f] hover:bg-[#2a4f7a] text-white min-w-[180px]"
                >
                  {generating ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Get Recommendations
                    </>
                  )}
                </Button>
              </div>
            </div>

            {loading ? (
              <p className="text-center text-gray-500 py-8">Loading recommended schedule...</p>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-8">
                <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2 font-medium">
                  Ready to generate your personalized schedule
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  {timePreference !== 'any'
                    ? `Click "Get Recommendations" above to generate recommendations for ${timePreference} time preference.`
                    : 'Select your preferred time above and click "Get Recommendations" to generate your personalized schedule.'}
                </p>
                {!user?.student_id && (
                  <p className="text-xs text-red-500 mt-2">
                    Please log in to generate recommendations
                  </p>
                )}
              </div>
            ) : (
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
                    {recommendedMWF.length > 0 ? (
                      recommendedMWF.map((course) => (
                        <CourseCard key={course.id} course={course} />
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm py-4 text-center">
                        No Monday/Wednesday/Friday courses
                      </p>
                    )}
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
                    {recommendedTTh.length > 0 ? (
                      recommendedTTh.map((course) => (
                        <CourseCard key={course.id} course={course} />
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm py-4 text-center">
                        No Tuesday/Thursday courses
                      </p>
                    )}
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
        onRemoveCourse={() => {
          // Read-only view in Schedule page
        }}
        onScheduleSaved={() => {
          loadDraftSchedules()
        }}
      />
    </div>
  )
}

