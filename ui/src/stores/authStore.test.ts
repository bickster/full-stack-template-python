import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useAuthStore from './authStore';
import { authApi, usersApi } from '../services/api';
import { mockUser, mockTokens } from '../test/utils';

// Mock the API
vi.mock('../services/api', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
  usersApi: {
    updateMe: vi.fn(),
    changePassword: vi.fn(),
    deleteMe: vi.fn(),
  },
}));

// Mock antd message
vi.mock('antd', () => ({
  message: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('authStore', () => {
  beforeEach(() => {
    // Clear all mocks
    vi.clearAllMocks();
    
    // Reset store state
    const { result } = renderHook(() => useAuthStore());
    act(() => {
      result.current.logout();
    });
    
    // Clear localStorage
    localStorage.clear();
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const loginResponse = {
        data: {
          user: mockUser,
          access_token: mockTokens.access_token,
          refresh_token: mockTokens.refresh_token,
          expires_in: 900,
        },
      };
      
      vi.mocked(authApi.login).mockResolvedValue(loginResponse);
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123',
        });
      });
      
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.tokens).toBeTruthy();
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      
      // Check localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'auth-tokens',
        expect.any(String)
      );
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'auth-user',
        JSON.stringify(mockUser)
      );
    });

    it('should handle login error', async () => {
      const error = {
        response: {
          data: {
            error: 'Invalid credentials',
          },
        },
      };
      
      vi.mocked(authApi.login).mockRejectedValue(error);
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        try {
          await result.current.login({
            email: 'test@example.com',
            password: 'wrong-password',
          });
        } catch {
          // Expected error
        }
      });
      
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      vi.mocked(authApi.register).mockResolvedValue({ data: {} });
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.register({
          email: 'new@example.com',
          username: 'newuser',
          password: 'password123',
        });
      });
      
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
      });
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      vi.mocked(authApi.logout).mockResolvedValue({ data: {} });
      
      const { result } = renderHook(() => useAuthStore());
      
      // Set initial authenticated state
      act(() => {
        result.current.user = mockUser;
        result.current.tokens = mockTokens;
        result.current.isAuthenticated = true;
      });
      
      await act(async () => {
        await result.current.logout();
      });
      
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth-tokens');
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth-user');
    });
  });

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const updatedUser = { ...mockUser, email: 'updated@example.com' };
      vi.mocked(usersApi.updateMe).mockResolvedValue({ data: updatedUser });
      
      const { result } = renderHook(() => useAuthStore());
      
      // Set initial user
      act(() => {
        result.current.user = mockUser;
      });
      
      await act(async () => {
        await result.current.updateUser({ email: 'updated@example.com' });
      });
      
      expect(result.current.user).toEqual(updatedUser);
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'auth-user',
        JSON.stringify(updatedUser)
      );
    });
  });

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      vi.mocked(usersApi.changePassword).mockResolvedValue({ data: {} });
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.changePassword({
          current_password: 'old-password',
          new_password: 'new-password',
        });
      });
      
      expect(usersApi.changePassword).toHaveBeenCalledWith({
        current_password: 'old-password',
        new_password: 'new-password',
      });
    });
  });

  describe('deleteAccount', () => {
    it('should delete account successfully', async () => {
      vi.mocked(usersApi.deleteMe).mockResolvedValue({ data: {} });
      
      const { result } = renderHook(() => useAuthStore());
      
      // Set initial authenticated state
      act(() => {
        result.current.user = mockUser;
        result.current.tokens = mockTokens;
        result.current.isAuthenticated = true;
      });
      
      await act(async () => {
        await result.current.deleteAccount();
      });
      
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth-tokens');
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth-user');
    });
  });
});