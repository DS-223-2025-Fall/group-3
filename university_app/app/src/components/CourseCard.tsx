import { Course } from '@/lib/api'
import { Button } from './ui/button'

interface CourseCardProps {
  course: Course
  showCode?: boolean
  showRemoveButton?: boolean
  onRemove?: (courseId: string) => void
}

export default function CourseCard({ 
  course, 
  showCode = false, 
  showRemoveButton = false,
  onRemove 
}: CourseCardProps) {
  return (
    <div className="border rounded-lg p-4 flex justify-between items-start bg-white hover:bg-gray-50 transition">
      <div className="flex-1">
        <h3 className="font-semibold text-lg">
          {showCode ? (
            <>{course.code} - {course.name}</>
          ) : (
            <span className="font-bold">{course.name}</span>
          )}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Section {course.section} •{' '}
          {course.instructorBioUrl ? (
            <a
              href={course.instructorBioUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#1e3a5f] hover:text-[#2a4f7a] underline-offset-2"
            >
              {course.instructor}
            </a>
          ) : (
            <span>{course.instructor}</span>
          )}
        </p>
        <p className="text-sm text-gray-600">
          {course.time}
        </p>
        <p className="text-sm text-gray-600">
          {course.location} • {course.duration} • {course.credits || 0} Credits
        </p>
        {course.cluster && course.cluster.length > 0 && (
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
        )}
      </div>
      {showRemoveButton && onRemove && (
        <Button
          variant="destructive"
          size="sm"
          onClick={() => onRemove(course.id)}
        >
          Remove
        </Button>
      )}
    </div>
  )
}

