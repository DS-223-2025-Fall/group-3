const instructorLinkedIn: Record<string, string> = {
  'Dr. Anna Martirosyan': 'https://www.linkedin.com/in/anna-martirosyan',
  'Dr. Narine Hovhannisyan': 'https://www.linkedin.com/in/narine-hovhannisyan',
  'Dr. Vardges Melkonian': 'https://www.linkedin.com/in/vardges-melkonian',
  'Dr. Tigran Harutyunyan': 'https://www.linkedin.com/in/tigran-harutyunyan',
  'Dr. Armen Petrosyan': 'https://www.linkedin.com/in/armen-petrosyan',
}

export const getInstructorLinkedIn = (name: string) =>
  instructorLinkedIn[name] ||
  `https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(
    name,
  )}`

