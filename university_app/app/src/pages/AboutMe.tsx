import { useEffect, useState, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { User } from 'lucide-react'
import { getStudentStanding } from '@/lib/utils'
import { fetchStudent, type Student } from '@/lib/api'

export default function AboutMe() {
  const { user } = useAuth()
  const [student, setStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadStudent = useCallback(async () => {
    if (!user?.student_id) {
      setLoading(false)
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const data = await fetchStudent(user.student_id)
      setStudent(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load student data')
      console.error('Error loading student:', err)
    } finally {
      setLoading(false)
    }
  }, [user?.student_id])

  useEffect(() => {
    loadStudent()
  }, [loadStudent])

  // Use fresh student data if available, otherwise fall back to user data from auth context
  const displayCredit = student?.credit ?? user?.credit ?? 0
  const displayProgram = student?.program_name ?? user?.program_name
  const displayName = student?.student_name ?? user?.student_name ?? user?.username
  const standing = getStudentStanding(displayCredit)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center gap-4 mb-6">
          <div className="h-20 w-20 rounded-full bg-[#1e3a5f] flex items-center justify-center">
            {user?.profilePhoto ? (
              <img
                src={user.profilePhoto}
                alt={user.student_name || user.username}
                className="h-full w-full rounded-full object-cover"
              />
            ) : (
              <User className="h-10 w-10 text-yellow-400" />
            )}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[#1e3a5f]">
              {displayName}
            </h1>
            <p className="text-gray-600">Student Profile</p>
          </div>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-600">Loading student information...</p>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">Error: {error}</p>
          </div>
        )}

        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Username</h3>
              <p className="text-xl text-[#1e3a5f]">{user?.username}</p>
            </div>

            {user?.student_id && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Student ID</h3>
                <p className="text-xl text-[#1e3a5f]">{user.student_id}</p>
              </div>
            )}

            {displayProgram && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Program</h3>
                <p className="text-xl text-[#1e3a5f]">{displayProgram}</p>
              </div>
            )}

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Credits</h3>
              <p className="text-xl text-[#1e3a5f]">{displayCredit}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Standing</h3>
              <p className="text-xl text-[#1e3a5f] font-semibold">{standing}</p>
            </div>
          </div>
        )}

        {!user?.student_id && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              Your account is not linked to a student profile. Please contact the administrator.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

