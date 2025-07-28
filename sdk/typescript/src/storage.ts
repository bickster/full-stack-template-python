/**
 * Token storage implementations
 */

import { AuthTokens, TokenStorage } from './types';

/**
 * In-memory token storage (suitable for Node.js applications)
 */
export class MemoryTokenStorage implements TokenStorage {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
  }

  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
  }
}

/**
 * LocalStorage token storage (for browser applications)
 */
export class LocalStorageTokenStorage implements TokenStorage {
  private readonly accessTokenKey = 'fullstack_access_token';
  private readonly refreshTokenKey = 'fullstack_refresh_token';

  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.accessTokenKey);
  }

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.refreshTokenKey);
  }

  setTokens(tokens: AuthTokens): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(this.accessTokenKey, tokens.access_token);
    localStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
  }

  clearTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
  }
}

/**
 * SessionStorage token storage (for browser applications with enhanced security)
 */
export class SessionStorageTokenStorage implements TokenStorage {
  private readonly accessTokenKey = 'fullstack_access_token';
  private readonly refreshTokenKey = 'fullstack_refresh_token';

  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return sessionStorage.getItem(this.accessTokenKey);
  }

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return sessionStorage.getItem(this.refreshTokenKey);
  }

  setTokens(tokens: AuthTokens): void {
    if (typeof window === 'undefined') return;
    sessionStorage.setItem(this.accessTokenKey, tokens.access_token);
    sessionStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
  }

  clearTokens(): void {
    if (typeof window === 'undefined') return;
    sessionStorage.removeItem(this.accessTokenKey);
    sessionStorage.removeItem(this.refreshTokenKey);
  }
}
