import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import Header from '@/components/Header'
import SearchFilters from '@/components/SearchFilters'
import CourseTable from '@/components/CourseTable'
import DraftSchedule from '@/components/DraftSchedule'
import { Course, fetchCourses, getUIPositions, trackUIClick, UIElementPosition } from '@/lib/api'
import { mockCourses } from '@/data/mockCourses'

const Index = () => {
  const [year, setYear] = useState('2024')
  const [semester, setSemester] = useState('Fall')
  const [courseType, setCourseType] = useState('All')
  const [searchText, setSearchText] = useState('')
  const [courses, setCourses] = useState<Course[]>(mockCourses)
  const [selectedCourses, setSelectedCourses] = useState<Set<string>>(new Set())
  const [isDraftOpen, setIsDraftOpen] = useState(false)
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null)
  const [uiConfig, setUiConfig] = useState<UIElementPosition | null>(null)
  const [studentId] = useState(1) // In production, get from auth context

  // Load UI positions on mount
  useEffect(() => {
    const loadUIPositions = async () => {
      try {
        const positions = await getUIPositions(studentId)
        setUiConfig(positions)
      } catch (error) {
        console.error('Failed to load UI positions:', error)
      }
    }
    loadUIPositions()
  }, [studentId])

  // Load courses on mount and when filters change
  useEffect(() => {
    loadCourses()
  }, [year, semester, courseType, searchText])

  const loadCourses = async () => {
    try {
      const fetchedCourses = await fetchCourses({
        year,
        semester,
        courseType: courseType === 'All' ? undefined : courseType,
        search: searchText || undefined,
      })
      
      if (fetchedCourses.length > 0) {
        setCourses(fetchedCourses)
      } else {
        // Use mock data if API doesn't return results
        let filtered = [...mockCourses]
        
        if (searchText) {
          filtered = filtered.filter(
            (c) =>
              c.name.toLowerCase().includes(searchText.toLowerCase()) ||
              c.code.toLowerCase().includes(searchText.toLowerCase())
          )
        }
        
        if (courseType !== 'All') {
          // Filter by course type if needed (mock data doesn't have this field)
        }
        
        setCourses(filtered)
      }
    } catch (error) {
      console.error('Error loading courses:', error)
      toast.error('Failed to load courses. Using mock data.')
      setCourses(mockCourses)
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
    // Track search button click
    if (uiConfig) {
      trackUIClick({
        student_id: studentId,
        element_type: 'button',
        element_id: 'search_button',
        element_position: uiConfig.ui_config.buttons,
        page_url: window.location.href
      })
    }
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

  const selectedCoursesList = courses.filter((c) => selectedCourses.has(c.id))

  return (
    <div className="min-h-screen bg-gray-50">
      <Header uiConfig={uiConfig} />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-[#1e3a5f] mb-2">
            Courses by Semester
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
          uiConfig={uiConfig}
          studentId={studentId}
        />

        <CourseTable
          courses={courses}
          selectedCourses={selectedCourses}
          onCourseSelect={handleCourseSelect}
          onClusterFilter={handleClusterFilter}
        />

        <DraftSchedule
          open={isDraftOpen}
          onOpenChange={setIsDraftOpen}
          selectedCourses={selectedCoursesList}
          onRemoveCourse={handleRemoveCourse}
        />
      </main>
    </div>
  )
}

export default Index

