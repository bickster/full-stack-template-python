/**
 * Full-Stack API TypeScript SDK
 * 
 * @packageDocumentation
 */

// Main client
export { FullStackClient } from './lib/client';

// API modules
export { AuthAPI } from './lib/auth-api';
export { UsersAPI } from './lib/users-api';

// Token storage
export {
  MemoryTokenStorage,
  LocalStorageTokenStorage,
  SessionStorageTokenStorage,
} from './lib/token-storage';

// Errors
export {
  ApiError,
  AuthError,
  ValidationError,
  NotFoundError,
  RateLimitError,
  NetworkError,
  TimeoutError,
} from './lib/errors';

// Types
export type {
  User,
  Token,
  LoginRequest,
  RegisterRequest,
  UpdateProfileRequest,
  DeleteAccountRequest,
  RefreshTokenRequest,
  ApiErrorResponse,
  RequestConfig,
  ClientConfig,
  TokenStorage,
  RequestInterceptor,
  ResponseInterceptor,
} from './types';

// Re-export commonly used types for convenience
export type ApiResponse<T> = Promise<T>;