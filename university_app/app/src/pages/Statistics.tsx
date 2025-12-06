import { BarChart3, TrendingUp, BookOpen, Users } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

export default function Statistics() {
  const { user } = useAuth()

  // Mock statistics - in a real app, these would come from the API
  const stats = {
    totalCredits: user?.credit || 0,
    coursesCompleted: 12,
    gpa: 3.7,
    coursesInProgress: 4,
  }

  const statCards = [
    {
      title: 'Total Credits',
      value: stats.totalCredits,
      icon: BookOpen,
      color: 'bg-blue-500',
    },
    {
      title: 'Courses Completed',
      value: stats.coursesCompleted,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      title: 'GPA',
      value: stats.gpa.toFixed(2),
      icon: BarChart3,
      color: 'bg-yellow-500',
    },
    {
      title: 'Courses In Progress',
      value: stats.coursesInProgress,
      icon: Users,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div>
      <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Statistics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-6 flex items-center gap-4"
            >
              <div className={`${stat.color} p-4 rounded-lg`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-500">{stat.title}</p>
                <p className="text-2xl font-bold text-[#1e3a5f]">{stat.value}</p>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-[#1e3a5f] mb-4">Academic Progress</h2>
        <p className="text-gray-600 mb-4">
          Track your academic progress and performance over time.
        </p>
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-500">
            Detailed statistics and charts will be available here in future updates.
          </p>
        </div>
      </div>
    </div>
  )
}

