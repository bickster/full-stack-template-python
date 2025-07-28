# API Integration Guide

This guide provides comprehensive information on integrating the FullStack API into various applications and frameworks.

## Table of Contents
1. [Integration Overview](#integration-overview)
2. [Framework-Specific Guides](#framework-specific-guides)
3. [Mobile Integration](#mobile-integration)
4. [Server-Side Integration](#server-side-integration)
5. [Webhook Integration](#webhook-integration)
6. [Testing Your Integration](#testing-your-integration)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring and Analytics](#monitoring-and-analytics)

## Integration Overview

### Key Integration Points

1. **Authentication**: JWT-based with automatic refresh
2. **API Client**: Available SDKs or direct HTTP calls
3. **Error Handling**: Consistent error format across all endpoints
4. **Rate Limiting**: Respect limits to avoid throttling
5. **Security**: HTTPS only, proper token storage

### Integration Checklist

- [ ] Choose integration method (SDK vs direct API)
- [ ] Set up authentication flow
- [ ] Implement error handling
- [ ] Configure token storage
- [ ] Add request/response logging
- [ ] Test error scenarios
- [ ] Monitor API usage

## Framework-Specific Guides

### React Integration

#### Setup
```bash
npm install @fullstack/api-client axios
```

#### Context Provider
```typescript
// contexts/ApiContext.tsx
import React, { createContext, useContext } from 'react';
import { FullStackClient, LocalStorageTokenStorage } from '@fullstack/api-client';

const ApiContext = createContext<FullStackClient | null>(null);

export function ApiProvider({ children }: { children: React.ReactNode }) {
  const client = new FullStackClient({
    baseURL: process.env.REACT_APP_API_URL!
  }, new LocalStorageTokenStorage());

  return (
    <ApiContext.Provider value={client}>
      {children}
    </ApiContext.Provider>
  );
}

export const useApi = () => {
  const client = useContext(ApiContext);
  if (!client) {
    throw new Error('useApi must be used within ApiProvider');
  }
  return client;
};
```

#### Custom Hooks
```typescript
// hooks/useUser.ts
import { useState, useEffect } from 'react';
import { User } from '@fullstack/api-client';
import { useApi } from '../contexts/ApiContext';

export function useUser() {
  const api = useApi();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (api.isAuthenticated()) {
      api.getCurrentUser()
        .then(setUser)
        .catch(setError)
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [api]);

  return { user, loading, error, refetch: () => api.getCurrentUser().then(setUser) };
}
```

#### Component Example
```typescript
// components/UserProfile.tsx
import React from 'react';
import { useUser } from '../hooks/useUser';
import { useApi } from '../contexts/ApiContext';

export function UserProfile() {
  const { user, loading, error } = useUser();
  const api = useApi();
  const [updating, setUpdating] = useState(false);

  const handleUpdate = async (data: UpdateUserRequest) => {
    setUpdating(true);
    try {
      await api.updateCurrentUser(data);
      // Refetch user data
      await refetch();
    } catch (error) {
      console.error('Update failed:', error);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>Not logged in</div>;

  return (
    <div>
      <h1>Profile</h1>
      <p>Username: {user.username}</p>
      <p>Email: {user.email}</p>
      {/* Update form */}
    </div>
  );
}
```

### Vue.js Integration

#### Setup
```bash
npm install @fullstack/api-client pinia
```

#### Pinia Store
```typescript
// stores/api.ts
import { defineStore } from 'pinia';
import { FullStackClient, User } from '@fullstack/api-client';

export const useApiStore = defineStore('api', {
  state: () => ({
    client: new FullStackClient({
      baseURL: import.meta.env.VITE_API_URL
    }),
    user: null as User | null,
    loading: false,
    error: null as Error | null
  }),

  getters: {
    isAuthenticated: (state) => state.client.isAuthenticated()
  },

  actions: {
    async login(username: string, password: string) {
      this.loading = true;
      this.error = null;
      try {
        await this.client.login({ username, password });
        this.user = await this.client.getCurrentUser();
      } catch (error) {
        this.error = error as Error;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      await this.client.logout();
      this.user = null;
    },

    async fetchUser() {
      if (this.isAuthenticated) {
        try {
          this.user = await this.client.getCurrentUser();
        } catch (error) {
          this.client.clearTokens();
        }
      }
    }
  }
});
```

#### Composable
```typescript
// composables/useApi.ts
import { computed } from 'vue';
import { useApiStore } from '@/stores/api';

export function useApi() {
  const store = useApiStore();

  return {
    client: store.client,
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    login: store.login,
    logout: store.logout
  };
}
```

### Angular Integration

#### Service
```typescript
// services/api.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { FullStackClient, User } from '@fullstack/api-client';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private client: FullStackClient;
  private userSubject = new BehaviorSubject<User | null>(null);
  public user$ = this.userSubject.asObservable();

  constructor() {
    this.client = new FullStackClient({
      baseURL: environment.apiUrl
    });

    this.checkAuth();
  }

  async login(username: string, password: string): Promise<void> {
    await this.client.login({ username, password });
    const user = await this.client.getCurrentUser();
    this.userSubject.next(user);
  }

  async logout(): Promise<void> {
    await this.client.logout();
    this.userSubject.next(null);
  }

  private async checkAuth(): Promise<void> {
    if (this.client.isAuthenticated()) {
      try {
        const user = await this.client.getCurrentUser();
        this.userSubject.next(user);
      } catch {
        this.client.clearTokens();
      }
    }
  }

  get isAuthenticated(): boolean {
    return this.client.isAuthenticated();
  }
}
```

#### Interceptor
```typescript
// interceptors/auth.interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler } from '@angular/common/http';
import { ApiService } from '../services/api.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private apiService: ApiService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const token = this.apiService.getAccessToken();

    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(req);
  }
}
```

## Mobile Integration

### React Native

```typescript
// api/client.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import { FullStackClient, TokenStorage, AuthTokens } from '@fullstack/api-client';

class AsyncStorageTokenStorage implements TokenStorage {
  async getAccessToken(): Promise<string | null> {
    return AsyncStorage.getItem('access_token');
  }

  async getRefreshToken(): Promise<string | null> {
    return AsyncStorage.getItem('refresh_token');
  }

  async setTokens(tokens: AuthTokens): Promise<void> {
    await AsyncStorage.setItem('access_token', tokens.access_token);
    await AsyncStorage.setItem('refresh_token', tokens.refresh_token);
  }

  async clearTokens(): Promise<void> {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
  }
}

export const apiClient = new FullStackClient({
  baseURL: 'https://api.example.com'
}, new AsyncStorageTokenStorage());
```

### Flutter

```dart
// lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  final Dio _dio;
  final FlutterSecureStorage _storage;

  ApiService()
    : _dio = Dio(BaseOptions(baseUrl: 'https://api.example.com')),
      _storage = FlutterSecureStorage() {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Handle token refresh
          final refreshToken = await _storage.read(key: 'refresh_token');
          if (refreshToken != null) {
            try {
              final tokens = await _refreshToken(refreshToken);
              await _saveTokens(tokens);

              // Retry request
              error.requestOptions.headers['Authorization'] = 'Bearer ${tokens['access_token']}';
              final response = await _dio.fetch(error.requestOptions);
              handler.resolve(response);
              return;
            } catch (e) {
              // Refresh failed
              await _clearTokens();
            }
          }
        }
        handler.next(error);
      },
    ));
  }

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _dio.post('/api/v1/auth/login', data: {
      'username': username,
      'password': password,
    });

    await _saveTokens(response.data);
    return response.data;
  }

  Future<void> _saveTokens(Map<String, dynamic> tokens) async {
    await _storage.write(key: 'access_token', value: tokens['access_token']);
    await _storage.write(key: 'refresh_token', value: tokens['refresh_token']);
  }
}
```

## Server-Side Integration

### Node.js/Express

```typescript
// middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import { FullStackClient } from '@fullstack/api-client';

interface AuthRequest extends Request {
  user?: User;
  apiClient?: FullStackClient;
}

export async function authMiddleware(
  req: AuthRequest,
  res: Response,
  next: NextFunction
) {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const client = new FullStackClient({
      baseURL: process.env.API_URL!
    });

    client.setTokens({
      access_token: token,
      refresh_token: '', // Not needed for validation
      token_type: 'bearer'
    });

    const user = await client.getCurrentUser();
    req.user = user;
    req.apiClient = client;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Python/Django

```python
# middleware.py
from django.http import JsonResponse
from fullstack_api import FullStackClient, AuthTokens

class FullStackAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

            client = FullStackClient(settings.FULLSTACK_API_URL)
            client.set_tokens(AuthTokens(
                access_token=token,
                refresh_token='',
                token_type='bearer'
            ))

            try:
                user = client.get_current_user()
                request.fullstack_user = user
                request.fullstack_client = client
            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
```

## Webhook Integration

### Webhook Security

```typescript
// webhook/handler.ts
import crypto from 'crypto';

interface WebhookPayload {
  event: string;
  data: any;
  timestamp: number;
}

function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const expectedSignature = hmac.digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

export async function handleWebhook(req: Request, res: Response) {
  const signature = req.headers['x-webhook-signature'] as string;
  const payload = JSON.stringify(req.body);

  if (!verifyWebhookSignature(payload, signature, process.env.WEBHOOK_SECRET!)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const { event, data } = req.body as WebhookPayload;

  switch (event) {
    case 'user.created':
      await handleUserCreated(data);
      break;
    case 'user.updated':
      await handleUserUpdated(data);
      break;
    case 'user.deleted':
      await handleUserDeleted(data);
      break;
    default:
      console.log('Unknown event:', event);
  }

  res.status(200).json({ received: true });
}
```

## Testing Your Integration

### Unit Tests

```typescript
// __tests__/api.test.ts
import { FullStackClient, MemoryTokenStorage } from '@fullstack/api-client';
import nock from 'nock';

describe('API Integration', () => {
  let client: FullStackClient;

  beforeEach(() => {
    client = new FullStackClient({
      baseURL: 'https://api.example.com'
    }, new MemoryTokenStorage());
  });

  afterEach(() => {
    nock.cleanAll();
  });

  test('login success', async () => {
    const mockTokens = {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer'
    };

    nock('https://api.example.com')
      .post('/api/v1/auth/login')
      .reply(200, mockTokens);

    const tokens = await client.login({
      username: 'test',
      password: 'password'
    });

    expect(tokens).toEqual(mockTokens);
    expect(client.isAuthenticated()).toBe(true);
  });

  test('handles 401 with token refresh', async () => {
    // Set initial tokens
    client.setTokens({
      access_token: 'expired-token',
      refresh_token: 'valid-refresh-token',
      token_type: 'bearer'
    });

    // First request fails with 401
    nock('https://api.example.com')
      .get('/api/v1/users/me')
      .matchHeader('authorization', 'Bearer expired-token')
      .reply(401);

    // Refresh token request
    nock('https://api.example.com')
      .post('/api/v1/auth/refresh')
      .reply(200, {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer'
      });

    // Retry with new token
    nock('https://api.example.com')
      .get('/api/v1/users/me')
      .matchHeader('authorization', 'Bearer new-access-token')
      .reply(200, {
        id: '123',
        username: 'testuser',
        email: 'test@example.com'
      });

    const user = await client.getCurrentUser();
    expect(user.username).toBe('testuser');
  });
});
```

### Integration Tests

```typescript
// __tests__/integration.test.ts
import { FullStackClient } from '@fullstack/api-client';

describe('API Integration Tests', () => {
  let client: FullStackClient;
  const testUser = {
    username: `test_${Date.now()}`,
    password: 'TestPassword123!',
    email: `test_${Date.now()}@example.com`
  };

  beforeAll(() => {
    client = new FullStackClient({
      baseURL: process.env.TEST_API_URL || 'http://localhost:8000'
    });
  });

  test('complete auth flow', async () => {
    // Register
    const user = await client.register({
      ...testUser,
      full_name: 'Test User'
    });
    expect(user.username).toBe(testUser.username);

    // Login
    const tokens = await client.login({
      username: testUser.username,
      password: testUser.password
    });
    expect(tokens.access_token).toBeDefined();

    // Get user
    const currentUser = await client.getCurrentUser();
    expect(currentUser.id).toBe(user.id);

    // Update user
    const updatedUser = await client.updateCurrentUser({
      full_name: 'Updated Name'
    });
    expect(updatedUser.full_name).toBe('Updated Name');

    // Change password
    await client.changePassword({
      old_password: testUser.password,
      new_password: 'NewPassword123!'
    });

    // Logout
    await client.logout();
    expect(client.isAuthenticated()).toBe(false);

    // Login with new password
    await client.login({
      username: testUser.username,
      password: 'NewPassword123!'
    });

    // Delete account
    await client.deleteAccount('NewPassword123!');
  });
});
```

## Performance Optimization

### Caching Strategy

```typescript
// cache/apiCache.ts
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class ApiCache {
  private cache = new Map<string, CacheEntry<any>>();

  set<T>(key: string, data: T, ttl: number = 300000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

// Usage with API client
class CachedApiClient extends FullStackClient {
  private cache = new ApiCache();

  async getCurrentUser(): Promise<User> {
    const cached = this.cache.get<User>('current_user');
    if (cached) return cached;

    const user = await super.getCurrentUser();
    this.cache.set('current_user', user, 60000); // 1 minute
    return user;
  }

  async updateCurrentUser(data: UpdateUserRequest): Promise<User> {
    const user = await super.updateCurrentUser(data);
    this.cache.invalidate('current_user');
    return user;
  }
}
```

### Request Debouncing

```typescript
// utils/debounce.ts
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeout: NodeJS.Timeout;
  let resolvePromise: (value: ReturnType<T>) => void;

  return (...args: Parameters<T>) => {
    return new Promise<ReturnType<T>>((resolve) => {
      clearTimeout(timeout);
      resolvePromise = resolve;

      timeout = setTimeout(async () => {
        const result = await func(...args);
        resolvePromise(result);
      }, wait);
    });
  };
}

// Usage
const debouncedSearch = debounce(
  (query: string) => apiClient.searchUsers(query),
  300
);
```

## Monitoring and Analytics

### Request Tracking

```typescript
// monitoring/tracker.ts
interface ApiMetrics {
  endpoint: string;
  method: string;
  duration: number;
  status: number;
  timestamp: number;
}

class ApiMonitor {
  private metrics: ApiMetrics[] = [];

  track(metrics: ApiMetrics): void {
    this.metrics.push(metrics);
    this.sendToAnalytics(metrics);
  }

  private sendToAnalytics(metrics: ApiMetrics): void {
    // Send to your analytics service
    if (window.gtag) {
      window.gtag('event', 'api_request', {
        event_category: 'API',
        event_label: `${metrics.method} ${metrics.endpoint}`,
        value: metrics.duration
      });
    }
  }

  getMetrics(): ApiMetrics[] {
    return this.metrics;
  }

  getAverageResponseTime(endpoint?: string): number {
    const relevant = endpoint
      ? this.metrics.filter(m => m.endpoint === endpoint)
      : this.metrics;

    if (relevant.length === 0) return 0;

    const sum = relevant.reduce((acc, m) => acc + m.duration, 0);
    return sum / relevant.length;
  }
}

// Integrate with API client
const monitor = new ApiMonitor();

axios.interceptors.request.use(config => {
  config.metadata = { startTime: Date.now() };
  return config;
});

axios.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.metadata.startTime;

    monitor.track({
      endpoint: response.config.url!,
      method: response.config.method!.toUpperCase(),
      duration,
      status: response.status,
      timestamp: Date.now()
    });

    return response;
  },
  error => {
    if (error.config?.metadata) {
      const duration = Date.now() - error.config.metadata.startTime;

      monitor.track({
        endpoint: error.config.url!,
        method: error.config.method!.toUpperCase(),
        duration,
        status: error.response?.status || 0,
        timestamp: Date.now()
      });
    }

    return Promise.reject(error);
  }
);
```

### Error Tracking

```typescript
// monitoring/errorTracker.ts
import * as Sentry from '@sentry/browser';

class ErrorTracker {
  static init(): void {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV,
      beforeSend(event, hint) {
        // Filter out expected errors
        if (event.exception) {
          const error = hint.originalException;

          // Don't send 401 errors
          if (error?.response?.status === 401) {
            return null;
          }

          // Add API context
          if (error?.config) {
            event.contexts = {
              ...event.contexts,
              api: {
                url: error.config.url,
                method: error.config.method,
                headers: error.config.headers
              }
            };
          }
        }

        return event;
      }
    });
  }

  static trackApiError(error: any): void {
    Sentry.captureException(error, {
      tags: {
        component: 'api',
        status: error.response?.status
      },
      extra: {
        url: error.config?.url,
        method: error.config?.method,
        data: error.response?.data
      }
    });
  }
}
```

## Best Practices Summary

1. **Always use HTTPS** in production
2. **Store tokens securely** (httpOnly cookies for web, secure storage for mobile)
3. **Implement proper error handling** with user-friendly messages
4. **Add request/response logging** for debugging
5. **Monitor API performance** and errors
6. **Implement caching** where appropriate
7. **Use request debouncing** for search/autocomplete
8. **Test error scenarios** including network failures
9. **Keep SDKs updated** for security patches
10. **Document your integration** for team members
