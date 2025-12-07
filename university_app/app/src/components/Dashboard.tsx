import { useState, useEffect } from 'react'
import { User, BookOpen, Calendar, BarChart3, LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import AboutMe from '@/pages/AboutMe'
import Classes from '@/pages/Classes'
import Schedule from '@/pages/Schedule'
import Statistics from '@/pages/Statistics'
import { Button } from './ui/button'

type Page = 'about' | 'classes' | 'schedule' | 'statistics'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activePage, setActivePage] = useState<Page>('about')
  const [renderKey, setRenderKey] = useState(0)

  // Force re-render when user changes to ensure all child components update
  // This is especially important after login when user state is set
  useEffect(() => {
    // Increment render key when user changes to force all child components to remount
    setRenderKey(prev => prev + 1)
  }, [user])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const menuItems = [
    { id: 'about' as Page, label: 'About me', icon: User },
    { id: 'classes' as Page, label: 'Classes', icon: BookOpen },
    { id: 'schedule' as Page, label: 'Schedule', icon: Calendar },
    { id: 'statistics' as Page, label: 'Statistics', icon: BarChart3 },
  ]

  const renderPage = () => {
    // Use renderKey to force remount when user changes
    const componentKey = `${user?.student_id || 'no-user'}-${renderKey}`
    
    switch (activePage) {
      case 'about':
        // Key ensures AboutMe re-renders when user changes (e.g., after login)
        return <AboutMe key={componentKey} />
      case 'classes':
        return <Classes key={componentKey} />
      case 'schedule':
        // Key ensures Schedule re-renders when user changes (e.g., after login)
        return <Schedule key={componentKey} />
      case 'statistics':
        return <Statistics key={componentKey} />
      default:
        return <AboutMe key={componentKey} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1e3a5f] text-white flex flex-col">
        <div className="p-6 border-b border-[#2a4a6f]">
          <h2 className="text-xl font-bold">Student Portal</h2>
          <p className="text-sm text-gray-300 mt-1">{user?.student_name || user?.username}</p>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = activePage === item.id
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActivePage(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-yellow-400 text-[#1e3a5f] font-semibold'
                        : 'text-gray-300 hover:bg-[#2a4a6f] hover:text-white'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </button>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-[#2a4a6f]">
          <Button
            onClick={handleLogout}
            variant="outline"
            className="w-full bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 border-0 flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            <span>Log Out</span>
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-6 py-8">
          {renderPage()}
        </div>
      </main>
    </div>
  )
}

