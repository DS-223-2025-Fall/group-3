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
import { Course } from '@/lib/api'
import { getInstructorLinkedIn } from '@/data/instructorLinks'
import { useAuth } from '@/contexts/AuthContext'
import { saveSchedule } from '@/lib/scheduleStorage'

interface DraftScheduleProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectedCourses: Course[]
  onRemoveCourse: (courseId: string) => void
  onScheduleSaved?: () => void
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

export default function DraftSchedule({
  open,
  onOpenChange,
  selectedCourses,
  onRemoveCourse,
  onScheduleSaved,
}: DraftScheduleProps) {
  const { isAuthenticated } = useAuth()

  const handleSaveSchedule = () => {
    if (!isAuthenticated) {
      toast.error('Please log in to save schedules')
      return
    }

    if (selectedCourses.length === 0) {
      toast.error('No courses to save')
      return
    }

    const saved = saveSchedule(selectedCourses)
    toast.success(`${saved.name} saved successfully!`)
    onScheduleSaved?.()
    onOpenChange(false)
  }
  // Group courses into MWF and TTh sections
  // A course that appears on any MWF day goes in MWF section
  // A course that appears on any TTh day goes in TTh section
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

  const mwfCourses = selectedCourses
    .filter((course) => isMWFCourse(course.days))
    .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

  const tthCourses = selectedCourses
    .filter((course) => isTThCourse(course.days))
    .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

  const renderCourseCard = (course: Course) => (
    <div
      key={course.id}
      className="border rounded-lg p-4 flex justify-between items-start bg-white hover:bg-gray-50 transition"
    >
      <div className="flex-1">
        <h3 className="font-semibold text-lg">
          {course.code} - {course.name}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Section {course.section} •{' '}
          <a
            href={getInstructorLinkedIn(course.instructor)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#1e3a5f] hover:text-[#2a4f7a] underline-offset-2"
          >
            {course.instructor}
          </a>
        </p>
        <p className="text-sm text-gray-600">
          {course.time}
        </p>
        <p className="text-sm text-gray-600">
          {course.location} • {course.duration} • {course.credits || 0} Credits
        </p>
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
      </div>
      <Button
        variant="destructive"
        size="sm"
        onClick={() => onRemoveCourse(course.id)}
      >
        Remove
      </Button>
    </div>
  )

  // Use selectedCourses.length instead of totalCourses to check if any courses are selected
  // This ensures we show courses even if they don't match MWF/TTh patterns
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
                    mwfCourses.map(renderCourseCard)
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
                    tthCourses.map(renderCourseCard)
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



