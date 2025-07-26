/**
 * FullStack API Client
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import {
  ApiConfig,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  User,
  UpdateUserRequest,
  ChangePasswordRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  ApiError,
  HealthCheck,
  RefreshTokenRequest,
  TokenStorage,
} from './types';
import { MemoryTokenStorage } from './storage';

export class FullStackClient {
  private readonly client: AxiosInstance;
  private readonly tokenStorage: TokenStorage;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor(config: ApiConfig, tokenStorage?: TokenStorage) {
    this.tokenStorage = tokenStorage || new MemoryTokenStorage();
    
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.tokenStorage.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                resolve(this.client(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = this.tokenStorage.getRefreshToken();
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            const tokens = await this.refreshAccessToken({ refresh_token: refreshToken });
            this.tokenStorage.setTokens(tokens);
            
            this.refreshSubscribers.forEach((callback) => callback(tokens.access_token));
            this.refreshSubscribers = [];

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
            }
            
            return this.client(originalRequest);
          } catch (refreshError) {
            this.tokenStorage.clearTokens();
            throw refreshError;
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/health');
    return response.data;
  }

  /**
   * Authentication endpoints
   */
  async login(data: LoginRequest): Promise<AuthTokens> {
    const response = await this.client.post<AuthTokens>('/api/v1/auth/login', data);
    const tokens = response.data;
    this.tokenStorage.setTokens(tokens);
    return tokens;
  }

  async register(data: RegisterRequest): Promise<User> {
    const response = await this.client.post<User>('/api/v1/auth/register', data);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout');
    } finally {
      this.tokenStorage.clearTokens();
    }
  }

  async refreshAccessToken(data: RefreshTokenRequest): Promise<AuthTokens> {
    const response = await this.client.post<AuthTokens>('/api/v1/auth/refresh', data);
    return response.data;
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>('/api/v1/auth/password-reset', data);
    return response.data;
  }

  async confirmPasswordReset(data: PasswordResetConfirm): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>('/api/v1/auth/password-reset/confirm', data);
    return response.data;
  }

  /**
   * User endpoints
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/v1/users/me');
    return response.data;
  }

  async updateCurrentUser(data: UpdateUserRequest): Promise<User> {
    const response = await this.client.patch<User>('/api/v1/users/me', data);
    return response.data;
  }

  async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>('/api/v1/users/me/change-password', data);
    return response.data;
  }

  async deleteAccount(password: string): Promise<{ message: string }> {
    const response = await this.client.delete<{ message: string }>('/api/v1/users/me', {
      data: { password }
    });
    this.tokenStorage.clearTokens();
    return response.data;
  }

  /**
   * Get current tokens
   */
  getTokens(): { accessToken: string | null; refreshToken: string | null } {
    return {
      accessToken: this.tokenStorage.getAccessToken(),
      refreshToken: this.tokenStorage.getRefreshToken(),
    };
  }

  /**
   * Set tokens manually (useful for SSR)
   */
  setTokens(tokens: AuthTokens): void {
    this.tokenStorage.setTokens(tokens);
  }

  /**
   * Clear tokens
   */
  clearTokens(): void {
    this.tokenStorage.clearTokens();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.tokenStorage.getAccessToken();
  }
}