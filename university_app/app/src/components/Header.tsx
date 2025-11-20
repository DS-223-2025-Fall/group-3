import { GraduationCap } from 'lucide-react'
import { Button } from './ui/button'

export default function Header() {
  return (
    <header className="bg-[#1e3a5f] text-white">
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
            <Button variant="outline" className="bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 border-0">
              Log In
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

