/**
 * Type definitions for the Full-Stack API SDK
 */

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Token {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  fullName?: string;
}

export interface UpdateProfileRequest {
  email?: string;
  fullName?: string;
}

export interface DeleteAccountRequest {
  password: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface ApiErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

export interface RequestConfig {
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

export interface ClientConfig {
  baseUrl: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  tokenStorage?: TokenStorage;
  onTokenRefresh?: (tokens: Token) => void;
}

export interface TokenStorage {
  getToken(): Promise<Token | null>;
  setToken(token: Token): Promise<void>;
  removeToken(): Promise<void>;
}

export type RequestInterceptor = (config: any) => any | Promise<any>;
export type ResponseInterceptor = {
  onFulfilled?: (response: any) => any | Promise<any>;
  onRejected?: (error: any) => any | Promise<any>;
};
