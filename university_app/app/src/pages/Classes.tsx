import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { fetchCourses, fetchPrograms, Course, Program } from '@/lib/api'
import SearchFilters from '@/components/SearchFilters'
import CourseTable from '@/components/CourseTable'
import DraftScheduleModal from '@/components/DraftSchedule'

export default function Classes() {
  const [year, setYear] = useState('All')
  const [semester, setSemester] = useState('All')
  const [courseType, setCourseType] = useState('All')
  const [searchText, setSearchText] = useState('')
  const [courses, setCourses] = useState<Course[]>([])
  const [programs, setPrograms] = useState<string[]>([])
  const [selectedCourses, setSelectedCourses] = useState<Set<string>>(new Set())
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null)
  const [isDraftModalOpen, setIsDraftModalOpen] = useState(false)

  useEffect(() => {
    loadPrograms()
  }, [])

  useEffect(() => {
    loadCourses()
  }, [year, semester, courseType, searchText])

  const loadPrograms = async () => {
    try {
      const fetchedPrograms = await fetchPrograms()
      const programNames = fetchedPrograms.map((p: Program) => p.prog_name)
      setPrograms(programNames)
    } catch (error) {
      console.error('Error loading programs:', error)
    }
  }

  const loadCourses = async () => {
    try {
      const fetchedCourses = await fetchCourses({
        year: year === 'All' ? undefined : year,
        semester: semester === 'All' ? undefined : semester,
        courseType: courseType === 'All' ? undefined : courseType,
        search: searchText || undefined,
      })
      
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
    if (cluster === selectedCluster) {
      loadCourses()
    } else {
      const filtered = courses.filter((c) => c.cluster.includes(cluster))
      setCourses(filtered)
    }
  }

  const handleDraftSchedule = () => {
    const selectedCourseList = courses.filter((c) => selectedCourses.has(c.id))
    if (selectedCourseList.length === 0) {
      toast.info('Please select at least one course to create a draft schedule')
      return
    }
    setIsDraftModalOpen(true)
  }

  const handleRemoveCourse = (courseId: string) => {
    const newSelected = new Set(selectedCourses)
    newSelected.delete(courseId)
    setSelectedCourses(newSelected)
    toast.success('Course removed from schedule')
  }

  const selectedCoursesList = courses.filter((c) => selectedCourses.has(c.id))

  return (
    <div>
      <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Classes</h1>
      
      <SearchFilters
        year={year}
        semester={semester}
        courseType={courseType}
        searchText={searchText}
        programs={programs}
        onYearChange={setYear}
        onSemesterChange={setSemester}
        onCourseTypeChange={setCourseType}
        onSearchTextChange={setSearchText}
        onDraftSchedule={handleDraftSchedule}
      />

      <CourseTable
        courses={courses}
        selectedCourses={selectedCourses}
        onCourseSelect={handleCourseSelect}
        onClusterFilter={handleClusterFilter}
        showCluster={courseType === 'GENED'}
      />

      <DraftScheduleModal
        open={isDraftModalOpen}
        onOpenChange={setIsDraftModalOpen}
        selectedCourses={selectedCoursesList}
        onRemoveCourse={handleRemoveCourse}
        onScheduleSaved={() => {
          toast.success('Draft schedule saved! You can view it in the Schedule page.')
        }}
      />
    </div>
  )
}

