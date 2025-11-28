import { GraduationCap } from 'lucide-react'
import { Button } from './ui/button'
import { UIElementPosition } from '@/lib/api'
import { trackUIClick } from '@/lib/api'

interface HeaderProps {
  uiConfig?: UIElementPosition | null
}

export default function Header({ uiConfig }: HeaderProps) {
  const headerColor = uiConfig?.ui_config.header_color || '#1e3a5f'
  
  const handleLoginClick = () => {
    if (uiConfig) {
      trackUIClick({
        student_id: uiConfig.student_id,
        element_type: 'button',
        element_id: 'login_button',
        element_position: uiConfig.ui_config.buttons,
        page_url: window.location.href
      })
    }
  }

  return (
    <header style={{ backgroundColor: headerColor }} className="text-white">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <GraduationCap className="h-8 w-8 text-yellow-400" />
            <div>
              <h1 className="text-xl font-bold">American University of Armenia</h1>
              <p className="text-sm text-gray-300">Student Portal</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-lg font-semibold">Courses by Semester</span>
            <Button 
              variant="outline" 
              className="bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 border-0"
              onClick={handleLoginClick}
            >
              Log In
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

