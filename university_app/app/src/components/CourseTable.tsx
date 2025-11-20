import { FileText } from 'lucide-react'
import { Course } from '@/lib/api'

export interface CourseTableProps {
  courses: Course[]
  selectedCourses: Set<string>
  onCourseSelect: (courseId: string) => void
  onClusterFilter?: (cluster: number) => void
}

export default function CourseTable({
  courses,
  selectedCourses,
  onCourseSelect,
  onClusterFilter,
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
              <th className="px-4 py-3 text-left text-sm font-semibold">Cluster</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Section</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Instructor</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Time</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Taken Seats</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Location</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Duration</th>
            </tr>
          </thead>
          <tbody>
            {courses.map((course, index) => (
              <tr
                key={course.id}
                className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              >
                <td className="px-4 py-3">
                  <input
                    type="radio"
                    name="course"
                    checked={selectedCourses.has(course.id)}
                    onChange={() => onCourseSelect(course.id)}
                    className="h-4 w-4 text-[#1e3a5f] focus:ring-[#1e3a5f]"
                  />
                </td>
                <td className="px-4 py-3">
                  {course.syllabusUrl && (
                    <a
                      href={`${API_BASE_URL}${course.syllabusUrl}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#1e3a5f] hover:text-[#2a4f7a]"
                    >
                      <FileText className="h-5 w-5" />
                    </a>
                  )}
                </td>
                <td className="px-4 py-3 text-sm font-medium">{course.code}</td>
                <td className="px-4 py-3 text-sm">{course.name}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2 flex-wrap">
                    {course.cluster.map((clusterNum) => (
                      <span
                        key={clusterNum}
                        onClick={() => onClusterFilter?.(clusterNum)}
                        className="px-2 py-1 bg-yellow-400 text-[#1e3a5f] rounded-full text-xs font-semibold cursor-pointer hover:bg-yellow-500"
                      >
                        {clusterNum}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">{course.section}</td>
                <td className="px-4 py-3 text-sm">{course.instructor}</td>
                <td className="px-4 py-3 text-sm">
                  <div>{course.days}</div>
                  <div className="text-gray-600">{course.time}</div>
                </td>
                <td className="px-4 py-3 text-sm">
                  {course.takenSeats}/{course.totalSeats}
                </td>
                <td className="px-4 py-3 text-sm">{course.location}</td>
                <td className="px-4 py-3 text-sm">{course.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

