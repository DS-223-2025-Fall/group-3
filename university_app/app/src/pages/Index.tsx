import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, BookOpen, Calendar, BarChart3, ArrowRight } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import Header from '@/components/Header'
import LoginModal from '@/components/LoginModal'
import { Button } from '@/components/ui/button'

const Index = () => {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [isLoginOpen, setIsLoginOpen] = useState(false)

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const features = [
    {
      icon: BookOpen,
      title: 'Browse Classes',
      description: 'Explore available courses and find the perfect schedule for your semester.',
    },
    {
      icon: Calendar,
      title: 'Schedule',
      description: 'View recommended schedules and manage your draft schedules.',
    },
    {
      icon: BarChart3,
      title: 'Track Progress',
      description: 'Monitor your academic progress, credits, and statistics all in one place.',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1e3a5f] via-[#2a4a6f] to-[#1e3a5f]">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16 mt-8">
            <div className="flex justify-center mb-6">
              <div className="bg-yellow-400 p-4 rounded-full">
                <GraduationCap className="h-16 w-16 text-[#1e3a5f]" />
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Welcome to AUA
          </h1>
            <p className="text-xl md:text-2xl text-gray-200 mb-2">
              Student Portal
            </p>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto mb-8">
              Access your courses, manage your schedule, and track your academic progress
            </p>
            <Button
              onClick={() => setIsLoginOpen(true)}
              size="lg"
              className="bg-yellow-400 text-[#1e3a5f] hover:bg-yellow-500 text-lg px-8 py-6 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Log In
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Features Section */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div
                  key={index}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  <div className="bg-yellow-400/20 p-3 rounded-lg w-fit mb-4">
                    <Icon className="h-8 w-8 text-yellow-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-300">{feature.description}</p>
                </div>
              )
            })}
          </div>

          {/* Additional Info */}
          <div className="mt-16 text-center">
            <p className="text-gray-300 text-sm">
              Need help? Contact the administration office for assistance with your account.
          </p>
          </div>
        </div>
      </main>
      <LoginModal open={isLoginOpen} onOpenChange={setIsLoginOpen} />
    </div>
  )
}

export default Index
