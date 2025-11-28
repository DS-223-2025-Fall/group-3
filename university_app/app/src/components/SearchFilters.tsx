import { Search } from 'lucide-react'
import { Input } from './ui/input'
import { Button } from './ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'
import { UIElementPosition } from '@/lib/api'
import { trackUIClick } from '@/lib/api'

interface SearchFiltersProps {
  year: string
  semester: string
  courseType: string
  searchText: string
  onYearChange: (year: string) => void
  onSemesterChange: (semester: string) => void
  onCourseTypeChange: (type: string) => void
  onSearchTextChange: (text: string) => void
  onSearch: () => void
  onDraftSchedule: () => void
  uiConfig?: UIElementPosition | null
  studentId: number
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
  onSearch,
  onDraftSchedule,
  uiConfig,
  studentId,
}: SearchFiltersProps) {
  const searchBarPosition = uiConfig?.ui_config.search_bar || 'top'
  const dropdownsPosition = uiConfig?.ui_config.dropdowns || 'left'
  const buttonsPosition = uiConfig?.ui_config.buttons || 'right'
  const searchButtonPosition = uiConfig?.ui_config.search_button_position || 'inline'

  const handleDropdownClick = (elementId: string) => {
    if (uiConfig) {
      trackUIClick({
        student_id: studentId,
        element_type: 'dropdown',
        element_id: elementId,
        element_position: dropdownsPosition,
        page_url: window.location.href
      })
    }
  }

  const handleDraftScheduleClick = () => {
    if (uiConfig) {
      trackUIClick({
        student_id: studentId,
        element_type: 'button',
        element_id: 'draft_schedule_button',
        element_position: buttonsPosition,
        page_url: window.location.href
      })
    }
    onDraftSchedule()
  }

  // Determine layout based on UI config
  const searchBarOrder = searchBarPosition === 'top' ? 'order-1' : 'order-3'
  const dropdownsOrder = dropdownsPosition === 'left' ? 'order-2' : 'order-4'
  const buttonsOrder = buttonsPosition === 'left' ? 'order-1' : 'order-3'

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="space-y-4">
        <div className={searchBarOrder}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search by Course Name
          </label>
          <div className={searchButtonPosition === 'inline' ? 'flex gap-2' : ''}>
            <Input
              type="text"
              placeholder="Type course name or code..."
              value={searchText}
              onChange={(e) => onSearchTextChange(e.target.value)}
              className="w-full"
              onFocus={() => {
                if (uiConfig) {
                  trackUIClick({
                    student_id: studentId,
                    element_type: 'search_bar',
                    element_id: 'search_input',
                    element_position: searchBarPosition,
                    page_url: window.location.href
                  })
                }
              }}
            />
            {searchButtonPosition === 'inline' && (
              <Button onClick={onSearch} className="bg-[#1e3a5f] hover:bg-[#2a4f7a]">
                <Search className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        
        <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 ${dropdownsOrder}`}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Year
            </label>
            <Select 
              value={year} 
              onValueChange={(value) => {
                handleDropdownClick('year_dropdown')
                onYearChange(value)
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2022">2022</SelectItem>
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
            <Select 
              value={semester} 
              onValueChange={(value) => {
                handleDropdownClick('semester_dropdown')
                onSemesterChange(value)
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
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
            <Select 
              value={courseType} 
              onValueChange={(value) => {
                handleDropdownClick('course_type_dropdown')
                onCourseTypeChange(value)
              }}
            >
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
        
        <div className={`flex gap-4 ${buttonsOrder === 'order-1' ? 'justify-start' : 'justify-end'}`}>
          {searchButtonPosition === 'separate' && (
            <Button onClick={onSearch} className="bg-[#1e3a5f] hover:bg-[#2a4f7a]">
              <Search className="mr-2 h-4 w-4" />
              Search
            </Button>
          )}
          <Button variant="outline" onClick={handleDraftScheduleClick}>
            Draft a Schedule
          </Button>
        </div>
      </div>
    </div>
  )
}

