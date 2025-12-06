import { useState } from 'react'
import { Calendar } from 'lucide-react'
import DraftScheduleModal from '@/components/DraftSchedule'

export default function DraftSchedule() {
  const [isDraftOpen, setIsDraftOpen] = useState(false)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-4xl font-bold text-[#1e3a5f]">Draft Schedule</h1>
        <button
          onClick={() => setIsDraftOpen(true)}
          className="bg-yellow-400 text-[#1e3a5f] px-6 py-2 rounded-lg font-semibold hover:bg-yellow-500 transition-colors flex items-center gap-2"
        >
          <Calendar className="h-5 w-5" />
          <span>View Draft Schedule</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <p className="text-gray-600 mb-4">
          Manage your draft schedule and plan your courses for the upcoming semester.
        </p>
        <p className="text-sm text-gray-500">
          Select courses from the Classes page to add them to your draft schedule.
        </p>
      </div>

      <DraftScheduleModal
        open={isDraftOpen}
        onOpenChange={setIsDraftOpen}
        selectedCourses={[]}
        onRemoveCourse={() => {}}
        onScheduleSaved={() => {}}
      />
    </div>
  )
}

