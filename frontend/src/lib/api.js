import axios from 'axios';
import {
  API_BASE_URLS,
  AUTH_ENDPOINTS,
  APP_ENDPOINTS,
  ADMIN_ENDPOINTS,
  STORAGE_KEYS,
  ROUTES,
} from './constants';

// ---------------------------------------------------------------------------
// Axios instances (base URLs from environment variables)
// ---------------------------------------------------------------------------

const AUTH_API = axios.create({
  baseURL: API_BASE_URLS.AUTH,
  headers: { 'Content-Type': 'application/json' },
});

const APP_API = axios.create({
  baseURL: API_BASE_URLS.APP,
});

const ADMIN_API = axios.create({
  baseURL: API_BASE_URLS.ADMIN,
  headers: { 'Content-Type': 'application/json' },
});

// ---------------------------------------------------------------------------
// Request interceptor – attach Bearer token
// ---------------------------------------------------------------------------

const addAuthToken = (config) => {
  const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
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

      const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      if (!refreshToken) {
        isRefreshing = false;
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        window.location.href = ROUTES.LOGIN;
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(
          `${API_BASE_URLS.AUTH}${AUTH_ENDPOINTS.REFRESH}`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        const tokens = data.data || data;
        const newAccessToken = tokens.access_token;
        const newRefreshToken = tokens.refresh_token;

        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);
        }

        processQueue(null, newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return instance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        window.location.href = ROUTES.LOGIN;
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
  register: (data) => AUTH_API.post(AUTH_ENDPOINTS.REGISTER, data),
  login: (data) => AUTH_API.post(AUTH_ENDPOINTS.LOGIN, data),
  logout: () => {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    return AUTH_API.post(AUTH_ENDPOINTS.LOGOUT, { refresh_token: refreshToken || null });
  },
  getMe: () => AUTH_API.get(AUTH_ENDPOINTS.ME),
  refresh: (refreshToken) => AUTH_API.post(AUTH_ENDPOINTS.REFRESH, { refresh_token: refreshToken }),
};

// ---------------------------------------------------------------------------
// Application API  (trailing slash on list endpoint to match FastAPI router)
// ---------------------------------------------------------------------------

export const appAPI = {
  uploadPhoto: (formData) => APP_API.post(APP_ENDPOINTS.UPLOAD, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getSubmissions: (params) => APP_API.get(APP_ENDPOINTS.LIST, { params }),
  getSubmission: (id) => APP_API.get(APP_ENDPOINTS.DETAIL(id)),
  deleteSubmission: (id) => APP_API.delete(APP_ENDPOINTS.DELETE(id)),
  getPhotoUrl: (submissionId) => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    return `${API_BASE_URLS.APP}${APP_ENDPOINTS.PHOTO(submissionId)}?token=${token}`;
  },
};

// ---------------------------------------------------------------------------
// Admin API
// ---------------------------------------------------------------------------

export const adminAPI = {
  getSubmissions: (params) => ADMIN_API.get(ADMIN_ENDPOINTS.SUBMISSIONS, { params }),
  getSubmission: (id) => ADMIN_API.get(ADMIN_ENDPOINTS.SUBMISSION_DETAIL(id)),
  getAnalytics: () => ADMIN_API.get(ADMIN_ENDPOINTS.ANALYTICS),
  getAuditLogs: (params) => ADMIN_API.get(ADMIN_ENDPOINTS.AUDIT_LOGS, { params }),
  exportCSV: (params) => ADMIN_API.get(ADMIN_ENDPOINTS.EXPORT_CSV, {
    params,
    responseType: 'blob',
  }),
  exportJSON: (params) => ADMIN_API.get(ADMIN_ENDPOINTS.EXPORT_JSON, {
    params,
    responseType: 'blob',
  }),
};

export default { authAPI, appAPI, adminAPI };
