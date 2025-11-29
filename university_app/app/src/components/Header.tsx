import { useState } from 'react'
import { GraduationCap, User } from 'lucide-react'
import { Button } from './ui/button'
import LoginModal from './LoginModal'
import { useAuth } from '@/contexts/AuthContext'

export default function Header() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <>
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
              {!isAuthenticated ? (
                <>
                  <span className="text-lg font-semibold transition-colors duration-200 hover:text-[#ffcc00] cursor-pointer">
                    Courses by Semester
                  </span>
                  <Button
                    variant="outline"
                    className="bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 border-0"
                    onClick={() => setIsLoginOpen(true)}
                  >
                    Log In
                  </Button>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-[#E6EDF4] flex items-center justify-center border-2 border-white">
                      {user?.profilePhoto ? (
                        <img
                          src={user.profilePhoto}
                          alt={user.name}
                          className="h-full w-full rounded-full object-cover"
                        />
                      ) : (
                        <User className="h-6 w-6 text-[#1e3a5f]" />
                      )}
                    </div>
                    <span className="text-lg font-semibold">{user?.name}</span>
                  </div>
                  <Button
                    variant="outline"
                    className="bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 border-0"
                    onClick={logout}
                  >
                    Log Out
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>
      <LoginModal open={isLoginOpen} onOpenChange={setIsLoginOpen} />
    </>
  )
}

