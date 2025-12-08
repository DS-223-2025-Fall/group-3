# APP Documentation

## Overview

The APP component is a React-based frontend application built with TypeScript and Vite.

## Technology Stack

- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI components

## Features

- Modern, responsive user interface
- Course browsing and search
- Student enrollment management
- Instructor information display
- Program and department navigation

## Development

To run the development server:

```bash
cd university_app/app
npm install
npm run dev
```

The app will be available at `http://localhost:5173` (or the configured port).

## Building

To build for production:

```bash
npm run build
```

## Docker

The app can be run in a Docker container with Nginx for serving static files. See the `Dockerfile` and `nginx.conf` in the `app` directory for details.

