import { Course } from '@/lib/api'

export interface SavedSchedule {
  id: string
  name: string
  courses: Course[]
  createdAt: string
}

const STORAGE_KEY = 'saved_schedules'

export function getSavedSchedules(): SavedSchedule[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    return JSON.parse(stored)
  } catch (e) {
    console.error('Failed to load saved schedules', e)
    return []
  }
}

export function saveSchedule(courses: Course[]): SavedSchedule {
  const existing = getSavedSchedules()
  const nextNumber = existing.length + 1
  const newSchedule: SavedSchedule = {
    id: `schedule-${Date.now()}`,
    name: `Schedule ${nextNumber}`,
    courses: [...courses],
    createdAt: new Date().toISOString(),
  }

  const updated = [...existing, newSchedule]
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
  return newSchedule
}

export function deleteSchedule(scheduleId: string): void {
  const existing = getSavedSchedules()
  const updated = existing.filter((s) => s.id !== scheduleId)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
}

