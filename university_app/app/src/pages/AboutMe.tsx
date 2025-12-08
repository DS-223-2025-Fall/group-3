import { useAuth } from '@/contexts/AuthContext'
import { User } from 'lucide-react'
import { getStudentStanding } from '@/lib/utils'

export default function AboutMe() {
  const { user } = useAuth()
  const standing = getStudentStanding(user?.credit)

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
              {user?.student_name || user?.username}
            </h1>
            <p className="text-gray-600">Student Profile</p>
          </div>
        </div>

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

          {user?.program_name && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Program</h3>
              <p className="text-xl text-[#1e3a5f]">{user.program_name}</p>
            </div>
          )}

          {user?.credit !== undefined && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Credits</h3>
              <p className="text-xl text-[#1e3a5f]">{user.credit || 0}</p>
            </div>
          )}

          {user?.credit !== undefined && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Standing</h3>
              <p className="text-xl text-[#1e3a5f] font-semibold">{standing}</p>
            </div>
          )}
        </div>

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

