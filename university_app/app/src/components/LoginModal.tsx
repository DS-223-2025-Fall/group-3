import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { useAuth } from '@/contexts/AuthContext'

interface LoginModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function LoginModal({ open, onOpenChange }: LoginModalProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    // Simple validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password')
      setIsLoading(false)
      return
    }

    try {
      // Use auth context login function (now async)
      const isValid = await login(username, password)

      if (!isValid) {
        setError('Incorrect username or password')
        setIsLoading(false)
        return
      }

      // Success - close modal, reset form, and navigate to dashboard
      onOpenChange(false)
      setUsername('')
      setPassword('')
      setError('')
      navigate('/dashboard')
    } catch (error) {
      setError('An error occurred during login. Please try again.')
      setIsLoading(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    onOpenChange(false)
    setUsername('')
    setPassword('')
    setError('')
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="bg-white rounded-lg shadow-lg max-w-md border border-gray-200">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-[#003B70]">
            Log In
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            Enter your credentials to access your account
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700"
            >
              Username
            </label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value)
                setError('')
              }}
              placeholder="Enter your username"
              className="w-full"
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setError('')
              }}
              placeholder="Enter your password"
              className="w-full"
              required
            />
          </div>

          {error && (
            <p className="text-sm text-[#C72C2C] mt-2">{error}</p>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              className="border-gray-300"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-[#003B70] hover:bg-[#FFCC00] hover:text-[#003B70] text-white transition-colors duration-200"
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Log In'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

