import { useState, useEffect } from 'react'
import { Calendar, ChevronDown, ChevronUp } from 'lucide-react'
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
import { getSavedSchedules, deleteSchedule, SavedSchedule } from '@/lib/scheduleStorage'
import { toast } from 'sonner'

interface SavedSchedulesProps {
  open: boolean
  onOpenChange: (open: boolean) => void
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
    className="border rounded-lg p-4 bg-gray-50"
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
        {course.days} • {course.time}
      </p>
      <p className="text-sm text-gray-600">
        {course.location} • {course.duration}
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
  </div>
)

export default function SavedSchedules({
  open,
  onOpenChange,
}: SavedSchedulesProps) {
  const [savedSchedules, setSavedSchedules] = useState<SavedSchedule[]>([])
  const [expandedSchedules, setExpandedSchedules] = useState<Set<string>>(new Set())

  // Load schedules when modal opens
  useEffect(() => {
    if (open) {
      const schedules = getSavedSchedules()
      setSavedSchedules(schedules)
      // Expand all by default
      const allIds = new Set(schedules.map((s) => s.id))
      setExpandedSchedules(allIds)
    }
  }, [open])

  const toggleSchedule = (scheduleId: string) => {
    const newExpanded = new Set(expandedSchedules)
    if (newExpanded.has(scheduleId)) {
      newExpanded.delete(scheduleId)
    } else {
      newExpanded.add(scheduleId)
    }
    setExpandedSchedules(newExpanded)
  }

  const handleDelete = (scheduleId: string) => {
    deleteSchedule(scheduleId)
    const updated = getSavedSchedules()
    setSavedSchedules(updated)
    toast.success('Schedule deleted')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Saved Schedules</DialogTitle>
          <DialogDescription>
            View and manage your saved course schedules
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 space-y-4">
          {savedSchedules.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No saved schedules yet. Save a schedule from the Draft Schedule modal to see it here.
            </p>
          ) : (
            savedSchedules.map((schedule) => {
              const mwfCourses = schedule.courses
                .filter((course) => isMWFCourse(course.days))
                .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

              const tthCourses = schedule.courses
                .filter((course) => isTThCourse(course.days))
                .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

              const isExpanded = expandedSchedules.has(schedule.id)

              return (
                <div
                  key={schedule.id}
                  className="border rounded-lg p-4 bg-white"
                >
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleSchedule(schedule.id)}
                  >
                    <h3 className="text-lg font-semibold text-[#1e3a5f]">
                      {schedule.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(schedule.id)
                        }}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5 text-[#1e3a5f]" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-[#1e3a5f]" />
                      )}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="mt-4 space-y-6">
                      {/* Monday / Wednesday / Friday Section */}
                      {mwfCourses.length > 0 && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-[#1e3a5f]" />
                            <h4 className="text-md font-semibold text-[#1e3a5f]">
                              Monday / Wednesday / Friday
                            </h4>
                          </div>
                          <div className="space-y-3 pl-7">
                            {mwfCourses.map(renderCourseCard)}
                          </div>
                        </div>
                      )}

                      {/* Separator */}
                      {mwfCourses.length > 0 && tthCourses.length > 0 && (
                        <div className="border-t border-gray-300 my-4" />
                      )}

                      {/* Tuesday / Thursday Section */}
                      {tthCourses.length > 0 && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-[#1e3a5f]" />
                            <h4 className="text-md font-semibold text-[#1e3a5f]">
                              Tuesday / Thursday
                            </h4>
                          </div>
                          <div className="space-y-3 pl-7">
                            {tthCourses.map(renderCourseCard)}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

