# Getting Started with FullStack API

This guide will help you get started with the FullStack API, from initial setup to making your first API calls.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [API Overview](#api-overview)
3. [Authentication](#authentication)
4. [Making Your First Request](#making-your-first-request)
5. [Using the SDKs](#using-the-sdks)
6. [Common Workflows](#common-workflows)
7. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:
- An API endpoint URL (e.g., `https://api.example.com`)
- A valid username and password for authentication
- One of the following:
  - Node.js 16+ (for JavaScript/TypeScript SDK)
  - Python 3.8+ (for Python SDK)
  - Any HTTP client (for direct API calls)

## API Overview

The FullStack API is a RESTful API that provides:
- **JWT-based authentication** with access and refresh tokens
- **User management** capabilities
- **Rate limiting** to prevent abuse
- **Comprehensive error handling**
- **Health monitoring** endpoints

### Base URL
All API requests should be made to:
```
https://api.example.com
```

### API Versioning
The current API version is `v1`. All endpoints are prefixed with `/api/v1`.

### Content Type
All requests and responses use JSON:
```
Content-Type: application/json
Accept: application/json
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Token Types
1. **Access Token**: Short-lived (15 minutes), used for API requests
2. **Refresh Token**: Long-lived (30 days), used to obtain new access tokens

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API

    Client->>API: POST /api/v1/auth/login
    Note over Client: {username, password}
    API-->>Client: {access_token, refresh_token}

    Client->>API: GET /api/v1/users/me
    Note over Client: Authorization: Bearer {access_token}
    API-->>Client: User data

    Note over Client: Access token expires

    Client->>API: POST /api/v1/auth/refresh
    Note over Client: {refresh_token}
    API-->>Client: {access_token, refresh_token}
```

## Making Your First Request

### 1. Register a New User (Optional)

```bash
curl -X POST https://api.example.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "SecurePassword123!",
    "full_name": "New User"
  }'
```

### 2. Login

```bash
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the Access Token

```bash
curl -X GET https://api.example.com/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Using the SDKs

### JavaScript/TypeScript

#### Installation
```bash
npm install @fullstack/api-client
```

#### Quick Start
```typescript
import { FullStackClient, LocalStorageTokenStorage } from '@fullstack/api-client';

const client = new FullStackClient({
  baseURL: 'https://api.example.com'
}, new LocalStorageTokenStorage());

// Login
await client.login({
  username: 'newuser',
  password: 'SecurePassword123!'
});

// Get user data
const user = await client.getCurrentUser();
console.log(`Hello, ${user.username}!`);
```

### Python

#### Installation
```bash
pip install fullstack-api-client
```

#### Quick Start
```python
from fullstack_api import FullStackClient, LoginRequest

client = FullStackClient("https://api.example.com")

# Login
client.login(LoginRequest(
    username="newuser",
    password="SecurePassword123!"
))

# Get user data
user = client.get_current_user()
print(f"Hello, {user.username}!")
```

## Common Workflows

### User Registration Flow

1. **Check if username/email is available** (client-side validation)
2. **Submit registration request**
3. **Handle validation errors** (e.g., password requirements)
4. **Auto-login after successful registration** (optional)
5. **Verify email address** (if email verification is enabled)

Example with error handling:
```typescript
try {
  const user = await client.register({
    email: 'user@example.com',
    username: 'newuser',
    password: 'password123',
    full_name: 'New User'
  });

  // Auto-login
  await client.login({
    username: 'newuser',
    password: 'password123'
  });
} catch (error) {
  if (error.code === 'VALIDATION_ERROR') {
    // Handle validation errors
    console.error('Validation failed:', error.details);
  }
}
```

### Handling Token Expiration

The SDKs automatically handle token refresh, but here's the manual flow:

```typescript
// Manual token refresh
try {
  const response = await fetch('/api/v1/users/me', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (response.status === 401) {
    // Token expired, refresh it
    const tokens = await refreshAccessToken(refreshToken);
    // Retry the request with new token
  }
} catch (error) {
  // Handle error
}
```

### Password Reset Flow

1. **Request password reset**
```typescript
await client.requestPasswordReset({
  email: 'user@example.com'
});
```

2. **User receives email with reset token**

3. **Confirm password reset with token**
```typescript
await client.confirmPasswordReset({
  token: 'reset-token-from-email',
  new_password: 'NewSecurePassword456!'
});
```

### Implementing Remember Me

Store the refresh token securely for persistent sessions:

```typescript
// Browser: Use LocalStorage
const client = new FullStackClient(config, new LocalStorageTokenStorage());

// Server: Use secure HTTP-only cookies
res.cookie('refresh_token', tokens.refresh_token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 30 * 24 * 60 * 60 * 1000 // 30 days
});
```

## Error Handling

### Error Response Format
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional context
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | Wrong username/password | 401 |
| `TOKEN_EXPIRED` | Access token expired | 401 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `USER_NOT_FOUND` | User doesn't exist | 404 |
| `INTERNAL_ERROR` | Server error | 500 |

### Rate Limiting

Authentication endpoints have rate limits:
- **Login**: 5 attempts per 15 minutes
- **Registration**: 5 attempts per hour
- **Password Reset**: 3 attempts per hour

Handle rate limits gracefully:
```typescript
try {
  await client.login(credentials);
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    const retryAfter = error.details.retry_after; // seconds
    console.log(`Please try again in ${retryAfter} seconds`);
  }
}
```

## Security Best Practices

### Token Storage
- **Browser**: Use `sessionStorage` for enhanced security or `localStorage` for persistence
- **Mobile**: Use secure device storage (Keychain on iOS, Keystore on Android)
- **Server**: Store in encrypted session or secure cookies

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### HTTPS Only
Always use HTTPS in production to prevent token interception.

### CORS Configuration
Ensure your domain is whitelisted in the API's CORS settings.

## Debugging Tips

### Enable Debug Logging
```typescript
// Check request/response details
client.on('request', (config) => console.log('Request:', config));
client.on('response', (response) => console.log('Response:', response));
```

### Common Issues

1. **401 Unauthorized**
   - Check if token is expired
   - Verify token is included in Authorization header
   - Ensure token format is correct: `Bearer <token>`

2. **422 Validation Error**
   - Check request body format
   - Verify all required fields are included
   - Check field types and constraints

3. **CORS Errors**
   - Verify your domain is allowed
   - Check preflight requests
   - Ensure credentials are included if needed

## Next Steps

Now that you're familiar with the basics:

1. **Explore the API Reference**: See all available endpoints in our [API documentation](/api/docs)
2. **Check Example Applications**: Learn from real-world implementations
3. **Read the Security Guide**: Understand how to secure your integration
4. **TypeScript Development**: Follow our [TypeScript Development Guide](TYPESCRIPT_DEVELOPMENT.md) for best practices
5. **Join the Community**: Get help and share your experience

## Need Help?

- 📚 [API Reference](/api/docs)
- 💬 [GitHub Discussions](https://github.com/yourusername/fullstack-app/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/fullstack-app/issues)
- 📧 [Contact Support](mailto:support@example.com)
