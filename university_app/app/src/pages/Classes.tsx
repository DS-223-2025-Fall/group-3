import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { fetchCourses, fetchPrograms, Course, Program } from '@/lib/api'
import SearchFilters from '@/components/SearchFilters'
import CourseTable from '@/components/CourseTable'
import DraftScheduleModal from '@/components/DraftSchedule'
import { checkTimeConflict } from '@/lib/utils'

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


  const handleCourseSelect = (courseId: string) => {
    const newSelected = new Set(selectedCourses)
    const course = courses.find((c) => c.id === courseId)

    if (!course) return

    if (newSelected.has(courseId)) {
      newSelected.delete(courseId)
      setSelectedCourses(newSelected)
      return
    }

    // Check for time conflicts with already selected courses
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
    setSelectedCourses(newSelected)
    toast.success(`${course.code} added to schedule`)
  }

  const handleClusterFilter = (cluster: number) => {
    if (cluster === selectedCluster) {
      // Deselect cluster - reload all courses
      setSelectedCluster(null)
      loadCourses()
    } else {
      // Select cluster - filter courses
      setSelectedCluster(cluster)
      const filtered = courses.filter((c) => c.cluster.includes(cluster))
      setCourses(filtered)
    }
  }

  const handleDraftSchedule = () => {
    if (selectedCourses.size === 0) {
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
        showCluster={courseType === 'GENED' || courseType === 'GenEd'}
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

