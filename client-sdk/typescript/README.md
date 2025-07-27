# Full-Stack API TypeScript SDK

A TypeScript SDK for interacting with the Full-Stack API, providing type-safe methods for authentication and user management.

## Installation

```bash
npm install @fullstack/api-client
# or
yarn add @fullstack/api-client
# or
pnpm add @fullstack/api-client
```

## Quick Start

```typescript
import { FullStackClient } from '@fullstack/api-client';

// Initialize the client
const client = new FullStackClient({
  baseUrl: 'https://api.example.com',
});

// Login
const { accessToken } = await client.auth.login({
  username: 'user@example.com',
  password: 'password123',
});

// Access protected resources
const user = await client.users.getCurrentUser();
console.log(`Logged in as: ${user.email}`);

// Logout
await client.auth.logout();
```

## Features

- 🔐 **Automatic token management** - Handles access/refresh token rotation
- 📘 **Full TypeScript support** - Complete type definitions
- 🚀 **Promise-based API** - Modern async/await interface
- 🛡️ **Type-safe errors** - Structured error types
- 🔄 **Auto-retry logic** - Built-in retry with exponential backoff
- 📦 **Tree-shakeable** - Only import what you use

## Usage

### Authentication

```typescript
import { FullStackClient, AuthError, ValidationError } from '@fullstack/api-client';

const client = new FullStackClient({
  baseUrl: 'https://api.example.com',
});

try {
  // Register a new user
  const user = await client.auth.register({
    email: 'newuser@example.com',
    username: 'newuser',
    password: 'SecurePass123!',
    fullName: 'New User',
  });

  // Login
  const tokens = await client.auth.login({
    username: 'newuser@example.com',
    password: 'SecurePass123!',
  });

  // Tokens are automatically stored and used for subsequent requests
  console.log('Logged in successfully');

} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation failed:', error.errors);
  } else if (error instanceof AuthError) {
    console.error('Authentication failed:', error.message);
  }
}
```

### User Management

```typescript
// Get current user
const me = await client.users.getCurrentUser();

// Update user profile
const updated = await client.users.updateProfile({
  fullName: 'Updated Name',
  email: 'newemail@example.com',
});

// Delete account
await client.users.deleteAccount({ password: 'SecurePass123!' });
```

### Error Handling

```typescript
import {
  FullStackClient,
  ApiError,
  AuthError,
  ValidationError,
  NotFoundError,
  RateLimitError,
} from '@fullstack/api-client';

try {
  const user = await client.users.getCurrentUser();
} catch (error) {
  if (error instanceof AuthError) {
    // Token expired or invalid
    await client.auth.refreshToken();
  } else if (error instanceof ValidationError) {
    // Invalid request data
    console.error('Validation errors:', error.errors);
  } else if (error instanceof RateLimitError) {
    // Too many requests
    console.error(`Rate limited. Retry after: ${error.retryAfter} seconds`);
  } else if (error instanceof NotFoundError) {
    // Resource not found
    console.error('User not found');
  } else if (error instanceof ApiError) {
    // General API error
    console.error(`API error: ${error.statusCode} - ${error.message}`);
  }
}
```

### Configuration

```typescript
import { FullStackClient } from '@fullstack/api-client';

const client = new FullStackClient({
  baseUrl: 'https://api.example.com',
  timeout: 30000, // Request timeout in milliseconds
  maxRetries: 3, // Number of retries for failed requests
  retryDelay: 1000, // Initial retry delay in milliseconds
  onTokenRefresh: (tokens) => {
    // Optional callback when tokens are refreshed
    console.log('Tokens refreshed');
  },
});
```

### TypeScript Types

All responses are fully typed:

```typescript
import type { User, Token, ApiResponse } from '@fullstack/api-client';

// Type-safe responses
const user: User = await client.users.getCurrentUser();
const tokens: Token = await client.auth.login({ username, password });

// Access nested types
type UserId = User['id'];
type UserEmail = User['email'];
```

### Interceptors

Add custom request/response interceptors:

```typescript
// Add request interceptor
client.addRequestInterceptor((config) => {
  console.log('Request:', config.method, config.url);
  return config;
});

// Add response interceptor
client.addResponseInterceptor(
  (response) => {
    console.log('Response:', response.status);
    return response;
  },
  (error) => {
    console.error('Error:', error.message);
    return Promise.reject(error);
  }
);
```

## Advanced Usage

### Custom Token Storage

By default, tokens are stored in memory. You can provide custom storage:

```typescript
import { FullStackClient, TokenStorage } from '@fullstack/api-client';

class LocalStorageTokenStorage implements TokenStorage {
  async getToken(): Promise<Token | null> {
    const token = localStorage.getItem('auth_token');
    return token ? JSON.parse(token) : null;
  }

  async setToken(token: Token): Promise<void> {
    localStorage.setItem('auth_token', JSON.stringify(token));
  }

  async removeToken(): Promise<void> {
    localStorage.removeItem('auth_token');
  }
}

const client = new FullStackClient({
  baseUrl: 'https://api.example.com',
  tokenStorage: new LocalStorageTokenStorage(),
});
```

### Cancellation

Cancel requests using AbortController:

```typescript
const controller = new AbortController();

// Start request
const promise = client.users.getCurrentUser({
  signal: controller.signal,
});

// Cancel request
controller.abort();

try {
  await promise;
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('Request was cancelled');
  }
}
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/fullstack-api-typescript.git
cd fullstack-api-typescript

# Install dependencies
npm install

# Build the SDK
npm run build

# Run tests
npm test
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch
```

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## API Reference

### Client

#### `new FullStackClient(config)`

Create a new API client instance.

**Parameters:**
- `config.baseUrl` (string, required): API base URL
- `config.timeout` (number, optional): Request timeout in milliseconds
- `config.maxRetries` (number, optional): Maximum number of retries
- `config.retryDelay` (number, optional): Initial retry delay
- `config.tokenStorage` (TokenStorage, optional): Custom token storage
- `config.onTokenRefresh` (function, optional): Token refresh callback

### Authentication

#### `client.auth.login(credentials)`

Login with username/email and password.

**Parameters:**
- `credentials.username` (string): Username or email
- `credentials.password` (string): Password

**Returns:** `Promise<Token>`

#### `client.auth.register(data)`

Register a new user.

**Parameters:**
- `data.email` (string): Email address
- `data.username` (string): Username
- `data.password` (string): Password
- `data.fullName` (string, optional): Full name

**Returns:** `Promise<User>`

#### `client.auth.refreshToken()`

Refresh the access token using the stored refresh token.

**Returns:** `Promise<Token>`

#### `client.auth.logout()`

Logout and clear stored tokens.

**Returns:** `Promise<void>`

### Users

#### `client.users.getCurrentUser()`

Get the current authenticated user.

**Returns:** `Promise<User>`

#### `client.users.updateProfile(data)`

Update the current user's profile.

**Parameters:**
- `data.email` (string, optional): New email
- `data.fullName` (string, optional): New full name

**Returns:** `Promise<User>`

#### `client.users.deleteAccount(data)`

Delete the current user's account.

**Parameters:**
- `data.password` (string): Current password for confirmation

**Returns:** `Promise<void>`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.