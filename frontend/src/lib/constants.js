// ---------------------------------------------------------------------------
// API Base URLs (from environment variables with local dev defaults)
// ---------------------------------------------------------------------------

export const API_BASE_URLS = {
  AUTH: import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001/api/v1',
  APP: import.meta.env.VITE_APP_API_URL || 'http://localhost:8002/api/v1',
  ADMIN: import.meta.env.VITE_ADMIN_API_URL || 'http://localhost:8003/api/v1',
};

// ---------------------------------------------------------------------------
// Auth Service Endpoints
// ---------------------------------------------------------------------------

export const AUTH_ENDPOINTS = {
  REGISTER: '/auth/register',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/users/me',
};

// ---------------------------------------------------------------------------
// Application Service Endpoints
// ---------------------------------------------------------------------------

export const APP_ENDPOINTS = {
  UPLOAD: '/submissions/upload',
  LIST: '/submissions/',
  DETAIL: (id) => `/submissions/${id}`,
  DELETE: (id) => `/submissions/${id}`,
  PHOTO: (id) => `/submissions/${id}/photo`,
};

// ---------------------------------------------------------------------------
// Admin Service Endpoints
// ---------------------------------------------------------------------------

export const ADMIN_ENDPOINTS = {
  SUBMISSIONS: '/admin/submissions',
  SUBMISSION_DETAIL: (id) => `/admin/submissions/${id}`,
  ANALYTICS: '/admin/analytics',
  AUDIT_LOGS: '/admin/audit-logs',
  EXPORT_CSV: '/admin/export/submissions/csv',
  EXPORT_JSON: '/admin/export/submissions/json',
};

// ---------------------------------------------------------------------------
// Local Storage Keys
// ---------------------------------------------------------------------------

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
};

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

export const ROUTES = {
  LOGIN: '/login',
};

// ---------------------------------------------------------------------------
// User Roles (must match backend UserRole enum values)
// ---------------------------------------------------------------------------

export const USER_ROLES = {
  USER: 'USER',
  ADMIN: 'ADMIN',
};
