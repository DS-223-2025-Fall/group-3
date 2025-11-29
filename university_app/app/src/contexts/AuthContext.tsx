import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  name: string
  username: string
  profilePhoto?: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => boolean
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

  const login = (username: string, password: string): boolean => {
    // Demo: Accept "admin"/"admin" or "student"/"password" as valid credentials
    const validCredentials = [
      { username: 'admin', password: 'admin', name: 'Admin User' },
      { username: 'student', password: 'password', name: 'John Smith' },
    ]

    const credential = validCredentials.find(
      (cred) => cred.username === username.trim() && cred.password === password.trim()
    )

    if (!credential) {
      return false
    }

    const newUser: User = {
      name: credential.name,
      username: credential.username,
      profilePhoto: undefined, // Could be a URL in production
    }

    setUser(newUser)
    localStorage.setItem('auth_user', JSON.stringify(newUser))
    return true
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

