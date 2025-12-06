import { Input } from './ui/input'
import { Button } from './ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'

interface SearchFiltersProps {
  year: string
  semester: string
  courseType: string
  searchText: string
  programs?: string[]
  onYearChange: (year: string) => void
  onSemesterChange: (semester: string) => void
  onCourseTypeChange: (type: string) => void
  onSearchTextChange: (text: string) => void
  onDraftSchedule: () => void
}

export default function SearchFilters({
  year,
  semester,
  courseType,
  searchText,
  onYearChange,
  onSemesterChange,
  onCourseTypeChange,
  onSearchTextChange,
  onDraftSchedule,
}: SearchFiltersProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div className="flex-1 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search by Course Name
            </label>
            <Input
              type="text"
              placeholder="Type course name or code..."
              value={searchText}
              onChange={(e) => onSearchTextChange(e.target.value)}
              className="w-full"
            />
          </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Year
            </label>
            <Select value={year} onValueChange={onYearChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All Years</SelectItem>
                <SelectItem value="2023">2023</SelectItem>
                <SelectItem value="2024">2024</SelectItem>
                <SelectItem value="2025">2025</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Semester
            </label>
            <Select value={semester} onValueChange={onSemesterChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All Semesters</SelectItem>
                <SelectItem value="Fall">Fall</SelectItem>
                <SelectItem value="Spring">Spring</SelectItem>
                <SelectItem value="Summer">Summer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Course Type
            </label>
            <Select value={courseType} onValueChange={onCourseTypeChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All</SelectItem>
                <SelectItem value="GenEd">GenEd</SelectItem>
                <SelectItem value="Major">Major</SelectItem>
                <SelectItem value="Elective">Elective</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        </div>
        <div className="flex flex-shrink-0 flex-col gap-3 sm:flex-row sm:gap-4 md:items-end md:justify-end">
          <Button
            variant="outline"
            onClick={onDraftSchedule}
            className="sm:w-auto bg-[#1e3a5f] text-white hover:bg-[#FFCC00] hover:text-[#1e3a5f] border-0"
          >
            Draft a Schedule
          </Button>
        </div>
      </div>
    </div>
  )
}

