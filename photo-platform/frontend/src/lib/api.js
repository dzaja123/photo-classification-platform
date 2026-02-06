import axios from 'axios';

// ---------------------------------------------------------------------------
// Axios instances
// ---------------------------------------------------------------------------

const AUTH_API = axios.create({
  baseURL: 'http://localhost:8001/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

const APP_API = axios.create({
  baseURL: 'http://localhost:8002/api/v1',
});

const ADMIN_API = axios.create({
  baseURL: 'http://localhost:8003/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// ---------------------------------------------------------------------------
// Request interceptor – attach Bearer token
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Response interceptor – automatic token refresh on 401
// ---------------------------------------------------------------------------

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
};

const createRefreshInterceptor = (instance) => {
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status !== 401 || originalRequest._retry) {
        return Promise.reject(error);
      }

      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return instance(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        isRefreshing = false;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(
          'http://localhost:8001/api/v1/auth/refresh',
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        const tokens = data.data || data;
        const newAccessToken = tokens.access_token;
        const newRefreshToken = tokens.refresh_token;

        localStorage.setItem('access_token', newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        processQueue(null, newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return instance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
  );
};

createRefreshInterceptor(AUTH_API);
createRefreshInterceptor(APP_API);
createRefreshInterceptor(ADMIN_API);

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const authAPI = {
  register: (data) => AUTH_API.post('/auth/register', data),
  login: (data) => AUTH_API.post('/auth/login', data),
  logout: () => {
    const refreshToken = localStorage.getItem('refresh_token');
    return AUTH_API.post('/auth/logout', { refresh_token: refreshToken || null });
  },
  getMe: () => AUTH_API.get('/users/me'),
  refresh: (refreshToken) => AUTH_API.post('/auth/refresh', { refresh_token: refreshToken }),
};

// ---------------------------------------------------------------------------
// Application API  (trailing slash on list endpoint to match FastAPI router)
// ---------------------------------------------------------------------------

export const appAPI = {
  uploadPhoto: (formData) => APP_API.post('/submissions/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getSubmissions: (params) => APP_API.get('/submissions/', { params }),
  getSubmission: (id) => APP_API.get(`/submissions/${id}`),
  deleteSubmission: (id) => APP_API.delete(`/submissions/${id}`),
};

// ---------------------------------------------------------------------------
// Admin API
// ---------------------------------------------------------------------------

export const adminAPI = {
  getSubmissions: (params) => ADMIN_API.get('/admin/submissions', { params }),
  getSubmission: (id) => ADMIN_API.get(`/admin/submissions/${id}`),
  getAnalytics: () => ADMIN_API.get('/admin/analytics'),
  getAuditLogs: (params) => ADMIN_API.get('/admin/audit-logs', { params }),
  exportCSV: (params) => ADMIN_API.get('/admin/export/submissions/csv', {
    params,
    responseType: 'blob',
  }),
  exportJSON: (params) => ADMIN_API.get('/admin/export/submissions/json', {
    params,
    responseType: 'blob',
  }),
};

export default { authAPI, appAPI, adminAPI };
