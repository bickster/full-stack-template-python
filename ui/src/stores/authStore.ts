import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { message } from 'antd';
import type {
  AuthStore,
  LoginRequest,
  RegisterRequest,
  UserUpdate,
  PasswordChangeRequest,
} from '../types';
import { authApi, usersApi } from '../services/api';
import type { AxiosError } from 'axios';

const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set, get) => ({
        // State
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        // Actions
        login: async (credentials: LoginRequest) => {
          set({ isLoading: true, error: null });
          try {
            const response = await authApi.login(credentials);
            const { user, access_token, refresh_token, expires_in } = response.data;
            
            const tokens = {
              access_token,
              refresh_token,
              expires_at: Date.now() + expires_in * 1000,
            };
            
            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            // Store tokens separately for interceptor
            localStorage.setItem('auth-tokens', JSON.stringify(tokens));
            localStorage.setItem('auth-user', JSON.stringify(user));
            
            message.success('Logged in successfully');
          } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            const errorMessage = axiosError.response?.data?.error || 'Login failed';
            set({
              isLoading: false,
              error: errorMessage,
            });
            message.error(errorMessage);
            throw error;
          }
        },

        register: async (data: RegisterRequest) => {
          set({ isLoading: true, error: null });
          try {
            await authApi.register(data);
            set({ isLoading: false, error: null });
            message.success('Registration successful! Please login.');
          } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            const errorMessage = axiosError.response?.data?.error || 'Registration failed';
            set({
              isLoading: false,
              error: errorMessage,
            });
            message.error(errorMessage);
            throw error;
          }
        },

        logout: async () => {
          set({ isLoading: true });
          try {
            await authApi.logout();
          } catch (error) {
            // Ignore logout errors
            console.error('Logout error:', error);
          } finally {
            // Clear state regardless
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
            
            // Clear storage
            localStorage.removeItem('auth-tokens');
            localStorage.removeItem('auth-user');
            
            message.success('Logged out successfully');
          }
        },

        refreshToken: async () => {
          const { tokens } = get();
          if (!tokens?.refresh_token) {
            throw new Error('No refresh token available');
          }

          try {
            const response = await authApi.refresh(tokens.refresh_token);
            const { access_token, expires_in } = response.data;
            
            const newTokens = {
              ...tokens,
              access_token,
              expires_at: Date.now() + expires_in * 1000,
            };
            
            set({ tokens: newTokens });
            
            // Update stored tokens
            localStorage.setItem('auth-tokens', JSON.stringify(newTokens));
          } catch (error) {
            // Token refresh failed, logout
            get().logout();
            throw error;
          }
        },

        updateUser: async (data: UserUpdate) => {
          set({ isLoading: true, error: null });
          try {
            const response = await usersApi.updateMe(data);
            const updatedUser = response.data;
            
            set({
              user: updatedUser,
              isLoading: false,
              error: null,
            });
            
            // Update stored user
            localStorage.setItem('auth-user', JSON.stringify(updatedUser));
            
            message.success('Profile updated successfully');
          } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            const errorMessage = axiosError.response?.data?.error || 'Update failed';
            set({
              isLoading: false,
              error: errorMessage,
            });
            message.error(errorMessage);
            throw error;
          }
        },

        changePassword: async (data: PasswordChangeRequest) => {
          set({ isLoading: true, error: null });
          try {
            await usersApi.changePassword(data);
            set({ isLoading: false, error: null });
            message.success('Password changed successfully');
          } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            const errorMessage = axiosError.response?.data?.error || 'Password change failed';
            set({
              isLoading: false,
              error: errorMessage,
            });
            message.error(errorMessage);
            throw error;
          }
        },

        deleteAccount: async () => {
          set({ isLoading: true, error: null });
          try {
            await usersApi.deleteMe();
            
            // Clear state
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
            
            // Clear storage
            localStorage.removeItem('auth-tokens');
            localStorage.removeItem('auth-user');
            
            message.success('Account deleted successfully');
          } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            const errorMessage = axiosError.response?.data?.error || 'Account deletion failed';
            set({
              isLoading: false,
              error: errorMessage,
            });
            message.error(errorMessage);
            throw error;
          }
        },

        clearError: () => set({ error: null }),
        
        setLoading: (loading: boolean) => set({ isLoading: loading }),
      }),
      {
        name: 'auth-store',
        partialize: (state) => ({
          user: state.user,
          tokens: state.tokens,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    )
  )
);

export default useAuthStore;