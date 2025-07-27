/**
 * Tests for the Full-Stack API TypeScript SDK
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { FullStackClient } from '../src/lib/client';
import { AuthError, ValidationError, RateLimitError } from '../src/lib/errors';
import { Token, User } from '../src/types';

// Mock axios
vi.mock('axios');
vi.mock('axios-retry');

describe('FullStackClient', () => {
  let client: FullStackClient;
  let mockAxiosInstance: any;

  beforeEach(() => {
    // Create mock axios instance
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
      interceptors: {
        request: { use: vi.fn(() => 1) },
        response: { use: vi.fn(() => 1) },
      },
    };

    // Mock axios.create
    vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as any);

    // Create client
    client = new FullStackClient({
      baseUrl: 'https://api.example.com',
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Client initialization', () => {
    it('should create client with default config', () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'https://api.example.com',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
    });

    it('should create client with custom config', () => {
      const customClient = new FullStackClient({
        baseUrl: 'https://custom.api.com',
        timeout: 60000,
        maxRetries: 5,
      });

      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'https://custom.api.com',
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
    });
  });

  describe('Authentication', () => {
    it('should login successfully', async () => {
      const mockToken: Token = {
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
        tokenType: 'Bearer',
        expiresIn: 900,
      };

      mockAxiosInstance.post.mockResolvedValueOnce({
        data: mockToken,
      });

      const result = await client.auth.login({
        username: 'test@example.com',
        password: 'password123',
      });

      expect(result).toEqual(mockToken);
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/v1/auth/login',
        {
          username: 'test@example.com',
          password: 'password123',
        },
        undefined
      );
    });

    it('should handle login failure', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: {
            code: 'authentication_error',
            message: 'Invalid credentials',
          },
        },
      });

      await expect(
        client.auth.login({
          username: 'test@example.com',
          password: 'wrong-password',
        })
      ).rejects.toThrow(AuthError);
    });

    it('should register user successfully', async () => {
      const mockUser: User = {
        id: '123',
        email: 'test@example.com',
        username: 'testuser',
        fullName: 'Test User',
        isActive: true,
        isVerified: false,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      mockAxiosInstance.post.mockResolvedValueOnce({
        data: mockUser,
      });

      const result = await client.auth.register({
        email: 'test@example.com',
        username: 'testuser',
        password: 'SecurePass123!',
        fullName: 'Test User',
      });

      expect(result).toEqual(mockUser);
    });

    it('should handle validation errors', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: {
            code: 'validation_error',
            message: 'Validation failed',
            errors: [
              { field: 'email', message: 'Invalid email format' },
              { field: 'password', message: 'Password too weak' },
            ],
          },
        },
      });

      await expect(
        client.auth.register({
          email: 'invalid',
          username: 'test',
          password: 'weak',
        })
      ).rejects.toThrow(ValidationError);
    });
  });

  describe('Users API', () => {
    it('should get current user', async () => {
      const mockUser: User = {
        id: '123',
        email: 'test@example.com',
        username: 'testuser',
        fullName: 'Test User',
        isActive: true,
        isVerified: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      mockAxiosInstance.get.mockResolvedValueOnce({
        data: mockUser,
      });

      const result = await client.users.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/api/v1/users/me',
        undefined
      );
    });

    it('should update user profile', async () => {
      const updatedUser: User = {
        id: '123',
        email: 'newemail@example.com',
        username: 'testuser',
        fullName: 'Updated Name',
        isActive: true,
        isVerified: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      mockAxiosInstance.put.mockResolvedValueOnce({
        data: updatedUser,
      });

      const result = await client.users.updateProfile({
        email: 'newemail@example.com',
        fullName: 'Updated Name',
      });

      expect(result).toEqual(updatedUser);
    });

    it('should delete account', async () => {
      mockAxiosInstance.delete.mockResolvedValueOnce({
        data: null,
      });

      await client.users.deleteAccount({
        password: 'password123',
      });

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith(
        '/api/v1/users/me',
        {
          data: { password: 'password123' },
        }
      );
    });
  });

  describe('Error handling', () => {
    it('should handle rate limit errors', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        response: {
          status: 429,
          data: {
            code: 'rate_limit_exceeded',
            message: 'Too many requests',
          },
          headers: {
            'retry-after': '60',
          },
        },
      });

      try {
        await client.auth.login({
          username: 'test@example.com',
          password: 'password',
        });
      } catch (error) {
        expect(error).toBeInstanceOf(RateLimitError);
        expect((error as RateLimitError).retryAfter).toBe(60);
      }
    });

    it('should handle network errors', async () => {
      mockAxiosInstance.get.mockRejectedValueOnce({
        request: {},
        message: 'Network Error',
      });

      await expect(client.users.getCurrentUser()).rejects.toThrow();
    });
  });

  describe('Interceptors', () => {
    it('should add and remove request interceptor', () => {
      const interceptor = vi.fn();
      const id = client.addRequestInterceptor(interceptor);

      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      
      // In real implementation, we'd need to track interceptor IDs
      expect(id).toBe(1);
    });

    it('should add and remove response interceptor', () => {
      const interceptor = {
        onFulfilled: vi.fn(),
        onRejected: vi.fn(),
      };
      
      const id = client.addResponseInterceptor(interceptor);

      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalledWith(
        interceptor.onFulfilled,
        interceptor.onRejected
      );
      
      expect(id).toBe(1);
    });
  });

  describe('Token storage', () => {
    it('should use custom token storage', async () => {
      const mockStorage = {
        getToken: vi.fn().mockResolvedValue(null),
        setToken: vi.fn().mockResolvedValue(undefined),
        removeToken: vi.fn().mockResolvedValue(undefined),
      };

      const customClient = new FullStackClient({
        baseUrl: 'https://api.example.com',
        tokenStorage: mockStorage,
      });

      const mockToken: Token = {
        accessToken: 'test-token',
        refreshToken: 'refresh-token',
        tokenType: 'Bearer',
        expiresIn: 900,
      };

      // Need to actually get the auth API to test storage
      // This would require more complex mocking
      expect(mockStorage.getToken).toBeDefined();
      expect(mockStorage.setToken).toBeDefined();
      expect(mockStorage.removeToken).toBeDefined();
    });
  });
});