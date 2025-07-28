import axios from 'axios';
import type { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { ApiError } from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokensStr = localStorage.getItem('auth-tokens');
    if (tokensStr) {
      try {
        const tokens = JSON.parse(tokensStr);
        if (tokens.access_token) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
      } catch (error) {
        console.error('Error parsing tokens:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for token refresh
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokensStr = localStorage.getItem('auth-tokens');
        if (!tokensStr) {
          throw new Error('No refresh token available');
        }

        const tokens = JSON.parse(tokensStr);
        const response = await api.post('/auth/refresh', {
          refresh_token: tokens.refresh_token,
        });

        const { access_token, expires_in } = response.data;
        
        // Update tokens in storage
        const newTokens = {
          ...tokens,
          access_token,
          expires_at: Date.now() + expires_in * 1000,
        };
        localStorage.setItem('auth-tokens', JSON.stringify(newTokens));

        // Notify subscribers and retry original request
        onTokenRefreshed(access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('auth-tokens');
        localStorage.removeItem('auth-user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/auth/register', data),
  
  logout: () =>
    api.post('/auth/logout'),
  
  refresh: (refresh_token: string) =>
    api.post('/auth/refresh', { refresh_token }),
};

export const usersApi = {
  getMe: () =>
    api.get('/users/me'),
  
  updateMe: (data: { email?: string; username?: string }) =>
    api.put('/users/me', data),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/users/me/change-password', data),
  
  deleteMe: () =>
    api.delete('/users/me'),
};

export default api;