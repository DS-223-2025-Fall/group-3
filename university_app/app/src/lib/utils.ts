import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Parse a time range string (e.g., "09:00-10:30") and return minutes since midnight
 * Returns Number.POSITIVE_INFINITY if parsing fails
 */
export function parseCourseTime(timeRange?: string): number {
  if (!timeRange) return Number.POSITIVE_INFINITY
  const [start] = timeRange.split('-')
  if (!start) return Number.POSITIVE_INFINITY
  const [hours = '0', minutes = '0'] = start.trim().split(':')
  const hourValue = parseInt(hours, 10)
  const minuteValue = parseInt(minutes, 10)
  if (Number.isNaN(hourValue) || Number.isNaN(minuteValue)) {
    return Number.POSITIVE_INFINITY
  }
  return hourValue * 60 + minuteValue
}

/**
 * Check if a course is scheduled on Monday, Wednesday, or Friday
 */
export function isMWFCourse(days?: string): boolean {
  if (!days) return false
  const normalizedDays = days.toLowerCase()
  return (
    normalizedDays.includes('monday') ||
    normalizedDays.includes('wednesday') ||
    normalizedDays.includes('friday')
  )
}

/**
 * Check if a course is scheduled on Tuesday or Thursday
 */
export function isTThCourse(days?: string): boolean {
  if (!days) return false
  const normalizedDays = days.toLowerCase()
  return (
    normalizedDays.includes('tuesday') ||
    normalizedDays.includes('thursday')
  )
}

/**
 * Parse time string to minutes (for time conflict checking)
 * Returns null if parsing fails
 */
export function parseTimeToMinutes(timeStr: string): number | null {
  const match = timeStr.match(/(\d{2}):(\d{2})/)
  if (!match) return null
  return parseInt(match[1]) * 60 + parseInt(match[2])
}

/**
 * Check if two courses have a time conflict
 */
export function checkTimeConflict(course1: { days?: string; time?: string }, course2: { days?: string; time?: string }): boolean {
  if (!course1.days || !course2.days || !course1.time || !course2.time) {
    return false
  }

  const days1 = course1.days.split(',').map((d) => d.trim())
  const days2 = course2.days.split(',').map((d) => d.trim())
  const hasCommonDay = days1.some((day) => days2.includes(day))

  if (!hasCommonDay) {
    return false
  }

  const [start1, end1] = course1.time.split('-').map(parseTimeToMinutes)
  const [start2, end2] = course2.time.split('-').map(parseTimeToMinutes)

  if (!start1 || !end1 || !start2 || !end2) {
    return false
  }

  return !(end1 <= start2 || end2 <= start1)
}

/**
 * Group courses into MWF and TTh arrays, sorted by time
 */
export function groupCoursesByDays<T extends { days?: string; time?: string }>(courses: T[]) {
  const mwfCourses = courses
    .filter((course) => isMWFCourse(course.days))
    .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

  const tthCourses = courses
    .filter((course) => isTThCourse(course.days))
    .sort((a, b) => parseCourseTime(a.time) - parseCourseTime(b.time))

  return { mwfCourses, tthCourses } as { mwfCourses: T[]; tthCourses: T[] }
}

/**
 * Calculate student standing based on credits
 */
export function getStudentStanding(credits: number | undefined): string {
  if (credits === undefined || credits === null) {
    return 'N/A'
  }
  if (credits < 30) {
    return 'Freshman'
  } else if (credits < 60) {
    return 'Sophomore'
  } else if (credits < 90) {
    return 'Junior'
  } else {
    return 'Senior'
  }
}

