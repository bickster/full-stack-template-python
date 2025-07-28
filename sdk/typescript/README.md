# FullStack API TypeScript/JavaScript Client

Official TypeScript/JavaScript client library for the FullStack API.

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
import { FullStackClient, LocalStorageTokenStorage } from '@fullstack/api-client';

// Create client instance
const client = new FullStackClient({
  baseURL: 'https://api.example.com',
}, new LocalStorageTokenStorage());

// Login
const tokens = await client.login({
  username: 'john_doe',
  password: 'password123'
});

// Get current user
const user = await client.getCurrentUser();
console.log('Hello,', user.username);
```

## Features

- 🔐 Automatic token management with refresh
- 🌐 Works in both Node.js and browsers
- 📝 Full TypeScript support
- 🔄 Automatic retry with token refresh
- 💾 Multiple token storage options
- 🚀 Promise-based API
- 🛡️ Built-in error handling

## Usage

### Creating a Client

```typescript
import { FullStackClient } from '@fullstack/api-client';

const client = new FullStackClient({
  baseURL: 'https://api.example.com',
  timeout: 30000, // Optional: request timeout in ms
  headers: {      // Optional: custom headers
    'X-Custom-Header': 'value'
  }
});
```

### Token Storage

The client supports different token storage strategies:

#### Browser - LocalStorage (Persistent)
```typescript
import { LocalStorageTokenStorage } from '@fullstack/api-client';

const client = new FullStackClient(config, new LocalStorageTokenStorage());
```

#### Browser - SessionStorage (Session only)
```typescript
import { SessionStorageTokenStorage } from '@fullstack/api-client';

const client = new FullStackClient(config, new SessionStorageTokenStorage());
```

#### Node.js / In-Memory (Default)
```typescript
import { MemoryTokenStorage } from '@fullstack/api-client';

const client = new FullStackClient(config, new MemoryTokenStorage());
// or simply
const client = new FullStackClient(config); // Uses MemoryTokenStorage by default
```

#### Custom Storage
```typescript
import { TokenStorage, AuthTokens } from '@fullstack/api-client';

class CustomTokenStorage implements TokenStorage {
  getAccessToken(): string | null {
    // Your implementation
  }

  getRefreshToken(): string | null {
    // Your implementation
  }

  setTokens(tokens: AuthTokens): void {
    // Your implementation
  }

  clearTokens(): void {
    // Your implementation
  }
}

const client = new FullStackClient(config, new CustomTokenStorage());
```

### Authentication

#### Register
```typescript
const user = await client.register({
  email: 'john@example.com',
  username: 'john_doe',
  password: 'SecurePassword123!',
  full_name: 'John Doe' // Optional
});
```

#### Login
```typescript
const tokens = await client.login({
  username: 'john_doe',
  password: 'SecurePassword123!'
});
// Tokens are automatically stored
```

#### Logout
```typescript
await client.logout();
// Tokens are automatically cleared
```

#### Check Authentication Status
```typescript
if (client.isAuthenticated()) {
  console.log('User is logged in');
}
```

### User Management

#### Get Current User
```typescript
const user = await client.getCurrentUser();
```

#### Update User Profile
```typescript
const updatedUser = await client.updateCurrentUser({
  email: 'newemail@example.com',
  full_name: 'John Smith'
});
```

#### Change Password
```typescript
await client.changePassword({
  old_password: 'OldPassword123!',
  new_password: 'NewPassword456!'
});
```

#### Delete Account
```typescript
await client.deleteAccount('currentPassword');
```

### Password Reset

#### Request Password Reset
```typescript
await client.requestPasswordReset({
  email: 'john@example.com'
});
```

#### Confirm Password Reset
```typescript
await client.confirmPasswordReset({
  token: 'reset-token-from-email',
  new_password: 'NewPassword789!'
});
```

### Health Check

```typescript
const health = await client.healthCheck();
console.log('API Status:', health.status);
console.log('Database:', health.database);
```

### Error Handling

```typescript
import { AxiosError } from '@fullstack/api-client';

try {
  await client.login({ username: 'john', password: 'wrong' });
} catch (error) {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data;
    console.error('Error:', apiError.error);
    console.error('Code:', apiError.code);

    // Handle specific error codes
    switch (apiError.code) {
      case 'INVALID_CREDENTIALS':
        console.log('Wrong username or password');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        console.log('Too many attempts, try again later');
        break;
      default:
        console.log('An error occurred');
    }
  }
}
```

### Manual Token Management

Sometimes you need to manage tokens manually (e.g., SSR, React Native):

```typescript
// Get current tokens
const { accessToken, refreshToken } = client.getTokens();

// Set tokens manually
client.setTokens({
  access_token: 'new-access-token',
  refresh_token: 'new-refresh-token',
  token_type: 'bearer'
});

// Clear tokens
client.clearTokens();
```

## API Reference

### FullStackClient

#### Constructor
```typescript
new FullStackClient(config: ApiConfig, tokenStorage?: TokenStorage)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `healthCheck()` | Check API health status | `Promise<HealthCheck>` |
| `login(data)` | Authenticate user | `Promise<AuthTokens>` |
| `register(data)` | Register new user | `Promise<User>` |
| `logout()` | Logout current user | `Promise<void>` |
| `refreshAccessToken(data)` | Refresh access token | `Promise<AuthTokens>` |
| `requestPasswordReset(data)` | Request password reset | `Promise<{message: string}>` |
| `confirmPasswordReset(data)` | Confirm password reset | `Promise<{message: string}>` |
| `getCurrentUser()` | Get current user info | `Promise<User>` |
| `updateCurrentUser(data)` | Update user profile | `Promise<User>` |
| `changePassword(data)` | Change password | `Promise<{message: string}>` |
| `deleteAccount(password)` | Delete user account | `Promise<{message: string}>` |
| `getTokens()` | Get current tokens | `{accessToken, refreshToken}` |
| `setTokens(tokens)` | Set tokens manually | `void` |
| `clearTokens()` | Clear stored tokens | `void` |
| `isAuthenticated()` | Check auth status | `boolean` |

## Examples

### React Example

```tsx
import React, { useState, useEffect } from 'react';
import { FullStackClient, LocalStorageTokenStorage, User } from '@fullstack/api-client';

const client = new FullStackClient({
  baseURL: process.env.REACT_APP_API_URL!
}, new LocalStorageTokenStorage());

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (client.isAuthenticated()) {
      client.getCurrentUser()
        .then(setUser)
        .catch(() => client.clearTokens())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = async (username: string, password: string) => {
    try {
      await client.login({ username, password });
      const user = await client.getCurrentUser();
      setUser(user);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    await client.logout();
    setUser(null);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {user ? (
        <div>
          <h1>Welcome, {user.username}!</h1>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <LoginForm onLogin={handleLogin} />
      )}
    </div>
  );
}
```

### Node.js Example

```javascript
const { FullStackClient } = require('@fullstack/api-client');

const client = new FullStackClient({
  baseURL: 'https://api.example.com'
});

async function main() {
  try {
    // Login
    await client.login({
      username: process.env.USERNAME,
      password: process.env.PASSWORD
    });

    // Get user data
    const user = await client.getCurrentUser();
    console.log('Logged in as:', user.username);

    // Perform operations...

    // Logout when done
    await client.logout();
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();
```

### Next.js Example (with SSR)

```typescript
// pages/api/[...proxy].ts
import { FullStackClient } from '@fullstack/api-client';
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const client = new FullStackClient({
    baseURL: process.env.API_URL!
  });

  // Get tokens from cookies
  const accessToken = req.cookies.access_token;
  const refreshToken = req.cookies.refresh_token;

  if (accessToken && refreshToken) {
    client.setTokens({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer'
    });
  }

  try {
    const user = await client.getCurrentUser();
    res.status(200).json(user);
  } catch (error) {
    res.status(401).json({ error: 'Unauthorized' });
  }
}
```

## Contributing

See the main repository's contributing guidelines.

## License

MIT
