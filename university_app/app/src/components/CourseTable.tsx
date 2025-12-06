import { FileText } from 'lucide-react'
import { Course } from '@/lib/api'
import { getInstructorLinkedIn } from '@/data/instructorLinks'

export interface CourseTableProps {
  courses: Course[]
  selectedCourses: Set<string>
  onCourseSelect: (courseId: string) => void
  onClusterFilter?: (cluster: number) => void
  showCluster: boolean
}

export default function CourseTable({
  courses,
  selectedCourses,
  onCourseSelect,
  onClusterFilter,
  showCluster,
}: CourseTableProps) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8008'

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[#1e3a5f] text-white">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold">Select</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Syllabus</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Course Code</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Course Name</th>
              {showCluster && (
                <th className="px-4 py-3 text-left text-sm font-semibold">Cluster</th>
              )}
              <th className="px-4 py-3 text-left text-sm font-semibold">Section</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Instructor</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">When Offered</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Time</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Credits</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Taken Seats</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Location</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Duration</th>
            </tr>
          </thead>
          <tbody>
            {courses.map((course, index) => {
              const isSelected = selectedCourses.has(course.id)
              const baseRowColor = index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
              const rowClass = isSelected ? 'bg-blue-50' : baseRowColor

              return (
                <tr
                  key={course.id}
                  onClick={() => onCourseSelect(course.id)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      onCourseSelect(course.id)
                    }
                  }}
                  tabIndex={0}
                  className={`${rowClass} cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 hover:bg-blue-50 transition`}
                >
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation()
                      onCourseSelect(course.id)
                    }}
                    aria-pressed={isSelected}
                    aria-label={`Select ${course.code}`}
                    className={`h-5 w-5 rounded-full border-2 flex items-center justify-center transition ${
                      isSelected
                        ? 'bg-[#1e3a5f] border-[#1e3a5f]'
                        : 'border-gray-400'
                    }`}
                  >
                    {isSelected && (
                      <span className="h-2 w-2 rounded-full bg-white" />
                    )}
                  </button>
                </td>
                <td className="px-4 py-3">
                  {course.syllabusUrl && (
                    <a
                      href={`${API_BASE_URL}${course.syllabusUrl}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#1e3a5f] hover:text-[#2a4f7a]"
                      onClick={(event) => event.stopPropagation()}
                    >
                      <FileText className="h-5 w-5" />
                    </a>
                  )}
                </td>
                <td className="px-4 py-3 text-sm font-medium">{course.code}</td>
                <td className="px-4 py-3 text-sm">{course.name}</td>
                {showCluster && (
                  <td className="px-4 py-3">
                    <div className="flex gap-2 flex-wrap">
                      {course.cluster.map((clusterNum) => (
                        <span
                          key={clusterNum}
                          onClick={(event) => {
                            event.stopPropagation()
                            onClusterFilter?.(clusterNum)
                          }}
                          className="px-2 py-1 bg-yellow-400 text-[#1e3a5f] rounded-full text-xs font-semibold cursor-pointer hover:bg-yellow-500"
                        >
                          {clusterNum}
                        </span>
                      ))}
                    </div>
                  </td>
                )}
                <td className="px-4 py-3 text-sm">{course.section}</td>
                <td className="px-4 py-3 text-sm">
                  <a
                    href={getInstructorLinkedIn(course.instructor)}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(event) => event.stopPropagation()}
                    className="text-[#1e3a5f] hover:text-[#2a4f7a] underline-offset-2"
                  >
                    {course.instructor}
                  </a>
                </td>
                <td className="px-4 py-3 text-sm">{course.semesterYear || 'N/A'}</td>
                <td className="px-4 py-3 text-sm">
                  <div>{course.days}</div>
                  <div className="text-gray-600">{course.time}</div>
                </td>
                <td className="px-4 py-3 text-sm">{course.credits || 0}</td>
                <td className="px-4 py-3 text-sm">
                  {course.takenSeats}/{course.totalSeats}
                </td>
                <td className="px-4 py-3 text-sm">{course.location}</td>
                <td className="px-4 py-3 text-sm">{course.duration}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

