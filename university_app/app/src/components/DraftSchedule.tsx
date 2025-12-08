import { Calendar } from 'lucide-react'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog'
import { Button } from './ui/button'
import { Course, createDraftSchedule, fetchDraftSchedules } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { groupCoursesByDays } from '@/lib/utils'
import CourseCard from './CourseCard'

interface DraftScheduleProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectedCourses: Course[]
  onRemoveCourse: (courseId: string) => void
  onScheduleSaved?: () => void
}

export default function DraftSchedule({
  open,
  onOpenChange,
  selectedCourses,
  onRemoveCourse,
  onScheduleSaved,
}: DraftScheduleProps) {
  const { isAuthenticated, user } = useAuth()

  const handleSaveSchedule = async () => {
    if (!isAuthenticated || !user?.student_id) {
      toast.error('Please log in to save schedules')
      return
    }

    if (selectedCourses.length === 0) {
      toast.error('No courses to save')
      return
    }

    try {
      // Convert course IDs (strings) to section IDs (numbers)
      const sectionIds = selectedCourses.map(course => parseInt(course.id))
      
      // Get existing schedules to determine next number
      const existingSchedules = await fetchDraftSchedules(user.student_id)
      
      const nextNumber = existingSchedules.length + 1
      const scheduleName = `Schedule ${nextNumber}`
      
      const saved = await createDraftSchedule({
        student_id: user.student_id,
        name: scheduleName,
        section_ids: sectionIds
      })
      
      toast.success(`${saved.name} saved successfully!`)
      onScheduleSaved?.()
      onOpenChange(false)
    } catch (error: any) {
      console.error('Error saving schedule:', error)
      toast.error(error.message || 'Failed to save schedule')
    }
  }
  // Group courses into MWF and TTh sections
  const { mwfCourses, tthCourses } = groupCoursesByDays(selectedCourses)
  const hasSelectedCourses = selectedCourses.length > 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Draft Schedule</DialogTitle>
          <DialogDescription>
            Review your selected courses and check for conflicts
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4">
          {!hasSelectedCourses ? (
            <p className="text-center text-gray-500 py-8">
              No courses selected yet. Select courses from the table to add them to your schedule.
            </p>
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
                  {mwfCourses.length > 0 ? (
                    mwfCourses.map((course) => (
                      <CourseCard
                        key={course.id}
                        course={course}
                        showCode
                        showRemoveButton
                        onRemove={onRemoveCourse}
                      />
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm py-4 text-center">
                      No Monday/Wednesday/Friday courses selected
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
                  {tthCourses.length > 0 ? (
                    tthCourses.map((course) => (
                      <CourseCard
                        key={course.id}
                        course={course}
                        showCode
                        showRemoveButton
                        onRemove={onRemoveCourse}
                      />
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm py-4 text-center">
                      No Tuesday/Thursday courses selected
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
          {hasSelectedCourses && isAuthenticated && (
            <Button
              className="bg-[#1e3a5f] hover:bg-[#FFCC00] hover:text-[#1e3a5f]"
              onClick={handleSaveSchedule}
            >
              Save Schedule
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}



