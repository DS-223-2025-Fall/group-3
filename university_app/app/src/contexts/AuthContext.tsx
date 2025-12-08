import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_BASE_URL } from '@/lib/api'

interface User {
  name: string
  username: string
  profilePhoto?: string
  student_name?: string
  student_id?: number
  program_name?: string
  credit?: number
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  // Load auth state from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('auth_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (e) {
        console.error('Failed to parse saved user', e)
      }
    }
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
        }),
      })

      if (!response.ok) {
        return false
      }

      const data = await response.json()
      
      const newUser: User = {
        name: data.student?.student_name || data.username,
        username: data.username,
        profilePhoto: undefined,
        student_name: data.student?.student_name,
        student_id: data.student_id,
        program_name: data.student?.program_name,
        credit: data.student?.credit,
      }

      setUser(newUser)
      localStorage.setItem('auth_user', JSON.stringify(newUser))
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('auth_user')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

