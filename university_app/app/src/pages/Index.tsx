import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { useAuth } from '@/contexts/AuthContext'
import Header from '@/components/Header'
import SearchFilters from '@/components/SearchFilters'
import CourseTable from '@/components/CourseTable'
import DraftSchedule from '@/components/DraftSchedule'
import SavedSchedules from '@/components/SavedSchedules'
import { Course, fetchCourses } from '@/lib/api'

const Index = () => {
  const { isAuthenticated } = useAuth()
  const [year, setYear] = useState('All')
  const [semester, setSemester] = useState('All')
  const [courseType, setCourseType] = useState('All')
  const [searchText, setSearchText] = useState('')
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourses, setSelectedCourses] = useState<Set<string>>(new Set())
  const [isDraftOpen, setIsDraftOpen] = useState(false)
  const [isSavedSchedulesOpen, setIsSavedSchedulesOpen] = useState(false)
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null)

  // Load courses on mount and when filters change
  useEffect(() => {
    loadCourses()
  }, [year, semester, courseType, searchText])

  const loadCourses = async () => {
    try {
      const fetchedCourses = await fetchCourses({
        year: year === 'All' ? undefined : year,
        semester: semester === 'All' ? undefined : semester,
        courseType: courseType === 'All' ? undefined : courseType,
        search: searchText || undefined,
      })
      
      // Always use real database data - no mock fallback
      setCourses(fetchedCourses)
      
      if (fetchedCourses.length === 0) {
        toast.info('No courses found for the selected filters.')
      }
    } catch (error) {
      console.error('Error loading courses:', error)
      toast.error('Failed to load courses from database.')
      setCourses([])
    }
  }

  const checkTimeConflict = (course1: Course, course2: Course): boolean => {
    if (!course1.days || !course2.days || !course1.time || !course2.time) {
      return false
    }

    const days1 = course1.days.split(',').map((d) => d.trim())
    const days2 = course2.days.split(',').map((d) => d.trim())
    const hasCommonDay = days1.some((day) => days2.includes(day))

    if (!hasCommonDay) {
      return false
    }

    const parseTime = (timeStr: string) => {
      const match = timeStr.match(/(\d{2}):(\d{2})/)
      if (!match) return null
      return parseInt(match[1]) * 60 + parseInt(match[2])
    }

    const [start1, end1] = course1.time.split('-').map(parseTime)
    const [start2, end2] = course2.time.split('-').map(parseTime)

    if (!start1 || !end1 || !start2 || !end2) {
      return false
    }

    return !(end1 <= start2 || end2 <= start1)
  }

  const handleCourseSelect = (courseId: string) => {
    const newSelected = new Set(selectedCourses)
    const course = courses.find((c) => c.id === courseId)

    if (!course) return

    if (newSelected.has(courseId)) {
      newSelected.delete(courseId)
    } else {
      // Check for time conflicts
      const selectedCourseList = courses.filter((c) => newSelected.has(c.id))
      const hasConflict = selectedCourseList.some((selectedCourse) =>
        checkTimeConflict(course, selectedCourse)
      )

      if (hasConflict) {
        toast.error(
          `Time conflict detected! ${course.code} conflicts with another selected course.`
        )
        return
      }

      newSelected.add(courseId)
      toast.success(`${course.code} added to schedule`)
    }

    setSelectedCourses(newSelected)
  }

  const handleClusterFilter = (cluster: number) => {
    setSelectedCluster(cluster === selectedCluster ? null : cluster)
    // Filter courses by cluster
    if (cluster === selectedCluster) {
      loadCourses()
    } else {
      const filtered = courses.filter((c) => c.cluster.includes(cluster))
      setCourses(filtered)
    }
  }

  const handleSearch = () => {
    loadCourses()
  }

  const handleDraftSchedule = () => {
    setIsDraftOpen(true)
  }

  const handleRemoveCourse = (courseId: string) => {
    const newSelected = new Set(selectedCourses)
    newSelected.delete(courseId)
    setSelectedCourses(newSelected)
    toast.success('Course removed from schedule')
  }

  // Filter courses that are in the selectedCourses Set
  // This ensures we only show courses that are actually in the current courses list
  const selectedCoursesList = courses.filter((c) => selectedCourses.has(c.id))

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6 md:ml-6">
          <h1 className="text-4xl font-bold text-[#1e3a5f] mb-2">
            {isAuthenticated ? 'Registration for Courses' : 'Courses by Semester'}
          </h1>
          <p className="text-gray-600">
            Browse and select courses for the {semester} {year} semester.
          </p>
        </div>

        <SearchFilters
          year={year}
          semester={semester}
          courseType={courseType}
          searchText={searchText}
          onYearChange={setYear}
          onSemesterChange={setSemester}
          onCourseTypeChange={setCourseType}
          onSearchTextChange={setSearchText}
          onSearch={handleSearch}
          onDraftSchedule={handleDraftSchedule}
          onSavedSchedules={() => setIsSavedSchedulesOpen(true)}
          isAuthenticated={isAuthenticated}
        />

        <CourseTable
          courses={courses}
          selectedCourses={selectedCourses}
          onCourseSelect={handleCourseSelect}
          onClusterFilter={handleClusterFilter}
          showCluster={courseType === 'GenEd'}
        />

        <DraftSchedule
          open={isDraftOpen}
          onOpenChange={setIsDraftOpen}
          selectedCourses={selectedCoursesList}
          onRemoveCourse={handleRemoveCourse}
          onScheduleSaved={() => {
            // Refresh saved schedules if modal is open
            if (isSavedSchedulesOpen) {
              // Force re-render by toggling
              setIsSavedSchedulesOpen(false)
              setTimeout(() => setIsSavedSchedulesOpen(true), 100)
            }
          }}
        />

        <SavedSchedules
          open={isSavedSchedulesOpen}
          onOpenChange={setIsSavedSchedulesOpen}
        />
      </main>
    </div>
  )
}

export default Index

