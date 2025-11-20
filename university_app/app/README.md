# University Frontend Application

React + TypeScript frontend for the American University of Armenia Student Portal.

## Features

- Course browsing and search
- Filter by year, semester, and course type
- Time conflict detection
- Schedule drafting
- Syllabus viewing
- Cluster-based filtering

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Sonner** - Toast notifications
- **React Router** - Routing

## Development

### Prerequisites

- Node.js 18+ and npm

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the `app` directory:

```env
VITE_API_URL=http://localhost:8008
```

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Docker

The frontend is containerized using Docker with a multi-stage build:

1. Build stage: Compiles the React app
2. Production stage: Serves the app using nginx

To build and run with Docker:

```bash
docker-compose up app
```

Or build the image manually:

```bash
docker build -t university-frontend .
docker run -p 5173:80 university-frontend
```

## Project Structure

```
app/
├── src/
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── Header.tsx
│   │   ├── SearchFilters.tsx
│   │   ├── CourseTable.tsx
│   │   └── DraftSchedule.tsx
│   ├── pages/           # Page components
│   │   └── Index.tsx
│   ├── lib/             # Utilities and API client
│   ├── data/            # Mock data
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile
```

## API Integration

The frontend expects the following API endpoints:

- `GET /sections` - Get course sections with optional query parameters:
  - `year` - Filter by year
  - `semester` - Filter by semester
  - `course_type` - Filter by course type
  - `search` - Search by course name or code

The API should return an array of course objects matching the `Course` interface defined in `src/lib/api.ts`.

If the API is unavailable, the app will fall back to mock data.

## Notes

- The app uses mock data by default if the API is not available
- Time conflict detection is implemented client-side
- Syllabus files are served from the API at `/syllabi/{filename}`
- The frontend is configured to work with the backend API running on port 8008

