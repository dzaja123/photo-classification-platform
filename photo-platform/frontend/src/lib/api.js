import axios from 'axios';

const AUTH_API = axios.create({
  baseURL: 'http://localhost:8001/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

const APP_API = axios.create({
  baseURL: 'http://localhost:8002/api/v1',
});

const ADMIN_API = axios.create({
  baseURL: 'http://localhost:8003/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
const addAuthToken = (config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

AUTH_API.interceptors.request.use(addAuthToken);
APP_API.interceptors.request.use(addAuthToken);
ADMIN_API.interceptors.request.use(addAuthToken);

// Auth API
export const authAPI = {
  register: (data) => AUTH_API.post('/auth/register', data),
  login: (data) => AUTH_API.post('/auth/login', data),
  logout: () => AUTH_API.post('/auth/logout'),
  getMe: () => AUTH_API.get('/auth/me'),
};

// Application API
export const appAPI = {
  uploadPhoto: (formData) => APP_API.post('/submissions/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getSubmissions: (params) => APP_API.get('/submissions', { params }),
  getSubmission: (id) => APP_API.get(`/submissions/${id}`),
  deleteSubmission: (id) => APP_API.delete(`/submissions/${id}`),
};

// Admin API
export const adminAPI = {
  getSubmissions: (params) => ADMIN_API.get('/admin/submissions', { params }),
  getSubmission: (id) => ADMIN_API.get(`/admin/submissions/${id}`),
  getAnalytics: () => ADMIN_API.get('/admin/analytics'),
  getAuditLogs: (params) => ADMIN_API.get('/admin/audit-logs', { params }),
  exportCSV: (params) => ADMIN_API.get('/admin/export/submissions/csv', { 
    params,
    responseType: 'blob'
  }),
  exportJSON: (params) => ADMIN_API.get('/admin/export/submissions/json', { 
    params,
    responseType: 'blob'
  }),
};

export default { authAPI, appAPI, adminAPI };
