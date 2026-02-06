# Photo Classification Platform - Frontend

React + Vite frontend for the Photo Classification Platform.

## Features

- User authentication (login/register)
- Photo upload with metadata
- View submission history
- Real-time classification results
- Admin dashboard
- Advanced filtering
- Analytics visualizations
- Data export

## Tech Stack

- React 18
- Vite 5
- TailwindCSS 3
- React Router v6
- Axios

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Development

The frontend runs on http://localhost:5173

API endpoints are configured to connect to:
- Auth Service: http://localhost:8001
- Application Service: http://localhost:8002
- Admin Service: http://localhost:8003

## Pages

### Public
- `/login` - User login
- `/register` - User registration

### User
- `/dashboard` - View submissions
- `/upload` - Upload new photo

### Admin
- `/admin` - Admin dashboard
- `/admin/submissions` - View all submissions with filters
- `/admin/analytics` - Analytics dashboard

## Components

- `Layout` - Main layout with navigation
- `AuthContext` - Authentication state management

## API Integration

All API calls are handled through `src/lib/api.js` which provides:
- `authAPI` - Authentication endpoints
- `appAPI` - Application endpoints
- `adminAPI` - Admin endpoints

## Environment

No environment variables needed for development.
All API URLs are hardcoded for local development.

For production, update API URLs in `src/lib/api.js`.
