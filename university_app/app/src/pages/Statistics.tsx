import { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, BookOpen, Users, GraduationCap, Clock } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { fetchStatistics, type Statistics } from '@/lib/api'
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar
} from 'recharts'

// Colors for charts
const COLORS = {
  primary: '#1e3a5f',
  success: '#4CAF50',
  warning: '#FFC107',
  info: '#2196F3',
  purple: '#9C27B0',
}

export default function Statistics() {
  const { user } = useAuth()
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (user?.student_id) {
      loadStatistics()
    } else {
      setLoading(false)
    }
  }, [user?.student_id])

  const loadStatistics = async () => {
    if (!user?.student_id) return
    
    setLoading(true)
    setError(null)
    try {
      const data = await fetchStatistics(user.student_id)
      setStatistics(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load statistics')
      console.error('Error loading statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  // Calculate overall GPA from GPA progress
  const overallGPA = statistics?.gpa_progress.length 
    ? (statistics.gpa_progress.reduce((sum, point) => sum + point.gpa, 0) / statistics.gpa_progress.length).toFixed(2)
    : '0.00'

  // Calculate courses completed
  const coursesCompleted = statistics?.course_completion.reduce((sum, prog) => sum + prog.taken, 0) || 0
  const coursesInProgress = 0 // This would need to come from current enrollments

  const statCards = [
    {
      title: 'Total Credits',
      value: statistics?.credits_progress.credit_earned || user?.credit || 0,
      icon: BookOpen,
      color: 'bg-blue-500',
    },
    {
      title: 'Courses Completed',
      value: coursesCompleted,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      title: 'GPA',
      value: overallGPA,
      icon: BarChart3,
      color: 'bg-yellow-500',
    },
    {
      title: 'Courses In Progress',
      value: coursesInProgress,
      icon: Users,
      color: 'bg-purple-500',
    },
  ]

  // Prepare data for credits donut chart
  const creditsData = statistics ? [
    { name: 'Earned', value: statistics.credits_progress.credit_earned, color: COLORS.success },
    { name: 'Remaining', value: statistics.credits_progress.remaining, color: COLORS.warning }
  ] : []

  // Prepare data for semester progress donut chart
  const semesterData = statistics ? [
    { name: 'Completed', value: statistics.semester_progress.percentage, color: COLORS.info },
    { name: 'Remaining', value: 100 - statistics.semester_progress.percentage, color: '#E0E0E0' }
  ] : []

  // Prepare data for course completion bar chart
  const courseCompletionData = statistics?.course_completion.map(prog => ({
    program: prog.program,
    completed: prog.taken,
    remaining: prog.remaining,
  })) || []

  if (!user?.student_id) {
    return (
      <div>
        <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Statistics</h1>
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-gray-600 text-center py-8">
            Please log in to view your statistics.
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Statistics</h1>
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-gray-600 text-center py-8">Loading statistics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Statistics</h1>
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-red-600 text-center py-8">Error: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-4xl font-bold text-[#1e3a5f] mb-6">Statistics</h1>

      {/* Summary Cards */}
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

      {/* GPA Progress Chart */}
      {statistics && statistics.gpa_progress.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">GPA Progress</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={statistics.gpa_progress}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="term" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                domain={[0, 4.0]}
                label={{ value: 'GPA', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="gpa" 
                stroke={COLORS.primary} 
                strokeWidth={2}
                dot={{ fill: COLORS.primary, r: 5 }}
                name="GPA"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Credits and Semester Progress */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Credits Earned Donut Chart */}
        {statistics && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="flex items-center gap-2 mb-6">
              <GraduationCap className="h-6 w-6 text-[#1e3a5f]" />
              <h2 className="text-2xl font-bold text-[#1e3a5f]">Credits Earned</h2>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={creditsData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {creditsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center mt-4">
              <p className="text-3xl font-bold text-[#1e3a5f]">
                {statistics.credits_progress.credit_earned}/{statistics.credits_progress.total_credits}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {statistics.credits_progress.remaining} credits remaining
              </p>
            </div>
          </div>
        )}

        {/* Semester Progress Donut Chart */}
        {statistics && (
      <div className="bg-white rounded-lg shadow-md p-8">
            <div className="flex items-center gap-2 mb-6">
              <Clock className="h-6 w-6 text-[#1e3a5f]" />
              <h2 className="text-2xl font-bold text-[#1e3a5f]">Semester Progress</h2>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={semesterData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  startAngle={90}
                  endAngle={-270}
                >
                  {semesterData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center mt-4">
              <p className="text-3xl font-bold text-[#1e3a5f]">
                {statistics.semester_progress.percentage.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {statistics.semester_progress.days_passed} of {statistics.semester_progress.days_total} days
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Course Completion by Program */}
      {statistics && statistics.course_completion.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="flex items-center gap-2 mb-6">
            <BookOpen className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Course Completion by Program</h2>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={courseCompletionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="program" 
                angle={-45}
                textAnchor="end"
                height={100}
              />
              <YAxis label={{ value: 'Number of Courses', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="completed" stackId="a" fill={COLORS.success} name="Completed" />
              <Bar dataKey="remaining" stackId="a" fill={COLORS.warning} name="Remaining" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Grade Distribution Histogram */}
      {statistics && statistics.grade_distribution.some(g => g.count > 0) && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Grade Distribution</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.grade_distribution.filter(g => g.count > 0)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="grade" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill={COLORS.primary}>
                {statistics.grade_distribution.filter(g => g.count > 0).map((entry, index) => {
                  let color = COLORS.success
                  if (entry.grade.startsWith('C') || entry.grade.startsWith('D') || entry.grade === 'F') {
                    color = '#f44336'
                  } else if (entry.grade.startsWith('B')) {
                    color = COLORS.warning
                  }
                  return <Cell key={`cell-${index}`} fill={color} />
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Performance by Course Type */}
      {statistics && statistics.performance_by_course_type.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Performance by Course Type</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.performance_by_course_type}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="course_type" />
              <YAxis domain={[0, 4.0]} label={{ value: 'Average GPA', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="average_gpa" fill={COLORS.info}>
                {statistics.performance_by_course_type.map((_, index) => {
                  const colors = [COLORS.primary, COLORS.success, COLORS.warning]
                  return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Time Slot Performance */}
      {statistics && statistics.time_slot_performance.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <Clock className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Performance by Time Slot</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.time_slot_performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time_slot" />
              <YAxis domain={[0, 4.0]} label={{ value: 'Average GPA', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="average_gpa" fill={COLORS.info}>
                {statistics.time_slot_performance.map((_, index) => {
                  const colors = [COLORS.warning, COLORS.info, COLORS.purple]
                  return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Course Load Per Semester */}
      {statistics && statistics.course_load.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <BookOpen className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Course Load Per Semester</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.course_load}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="term" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis label={{ value: 'Credits', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="credits" fill={COLORS.primary} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Prerequisites Completion Status */}
      {statistics && statistics.prerequisites_status.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <BookOpen className="h-6 w-6 text-[#1e3a5f]" />
            <h2 className="text-2xl font-bold text-[#1e3a5f]">Prerequisites Completion Status</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {statistics.prerequisites_status.slice(0, 12).map((prereq, index) => (
              <div key={index} className="border rounded-lg p-3 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-[#1e3a5f] text-sm flex-1">{prereq.course_name}</h3>
                  <span className="text-xs text-gray-600 ml-2 whitespace-nowrap">
                    {prereq.prerequisites_completed}/{prereq.prerequisites_total}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        prereq.completion_percentage === 100 
                          ? 'bg-green-500' 
                          : prereq.completion_percentage > 50 
                          ? 'bg-blue-500' 
                          : 'bg-yellow-500'
                      }`}
                      style={{ width: `${prereq.completion_percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-medium text-gray-700 min-w-[3rem] text-right">
                    {prereq.completion_percentage.toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Data Message */}
      {statistics && 
       statistics.gpa_progress.length === 0 && 
       statistics.course_completion.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-gray-600 text-center py-8">
            No statistics available yet. Complete some courses to see your progress!
          </p>
        </div>
      )}
    </div>
  )
}
