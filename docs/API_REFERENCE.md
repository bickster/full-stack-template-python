# Full-Stack API Reference

## Overview

The Full-Stack API provides secure authentication and user management functionality via a RESTful interface. All requests and responses use JSON format.

Base URL: `https://api.example.com`

## Authentication

The API uses JWT (JSON Web Token) authentication. After logging in, you'll receive an access token and a refresh token.

- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (30 days), used to obtain new access tokens

Include the access token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **General endpoints**: 60 requests per minute
- **Login endpoint**: 5 attempts per 15 minutes per IP/email

When rate limited, you'll receive a `429 Too Many Requests` response with a `Retry-After` header.

## Error Responses

All error responses follow this format:

```json
{
  "code": "error_code",
  "message": "Human-readable error message",
  "details": {
    "additional": "information"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 422 | Request validation failed |
| `authentication_error` | 401 | Authentication failed or token invalid |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `server_error` | 500 | Internal server error |

## Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"  // optional
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Validation Rules:**
- Email: Valid email format, unique
- Username: 3-50 characters, alphanumeric + underscore, unique
- Password: 8+ characters, must contain uppercase, lowercase, number, and special character
- Full name: 1-100 characters (optional)

**Error Responses:**
- `422`: Validation error (invalid email, weak password, duplicate user)

---

#### POST /api/v1/auth/login

Login with email/username and password.

**Request Body:**
```json
{
  "username": "johndoe",  // or email
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900  // seconds
}
```

**Error Responses:**
- `401`: Invalid credentials
- `422`: Validation error
- `429`: Too many login attempts

---

#### POST /api/v1/auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `401`: Invalid or expired refresh token

---

#### POST /api/v1/auth/logout

Logout and invalidate tokens.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response (204 No Content):**
No response body.

**Note:** This endpoint will always return 204, even if the token is already invalid.

---

### User Endpoints

#### GET /api/v1/users/me

Get current authenticated user's profile.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z"
}
```

**Error Responses:**
- `401`: Not authenticated

---

#### PUT /api/v1/users/me

Update current user's profile.

**Headers:**
- `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "email": "newemail@example.com",  // optional
  "full_name": "Jane Doe"  // optional
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "username": "johndoe",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_verified": false,  // reset if email changed
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T15:45:00Z"
}
```

**Validation Rules:**
- Email: Valid format, unique
- Full name: 1-100 characters

**Error Responses:**
- `401`: Not authenticated
- `422`: Validation error

**Note:** Changing email address will reset email verification status.

---

#### DELETE /api/v1/users/me

Delete current user's account.

**Headers:**
- `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "password": "SecurePass123!"  // Current password for confirmation
}
```

**Response (204 No Content):**
No response body.

**Error Responses:**
- `401`: Not authenticated or incorrect password
- `422`: Validation error

**Note:** This action is irreversible. All user data will be permanently deleted.

---

## Data Types

### User Object

```typescript
{
  id: string;           // UUID
  email: string;        // Email address
  username: string;     // Unique username
  full_name?: string;   // Optional full name
  is_active: boolean;   // Account active status
  is_verified: boolean; // Email verification status
  created_at: string;   // ISO 8601 timestamp
  updated_at: string;   // ISO 8601 timestamp
}
```

### Token Object

```typescript
{
  access_token: string;  // JWT access token
  refresh_token: string; // JWT refresh token
  token_type: string;    // Always "Bearer"
  expires_in: number;    // Seconds until expiration
}
```

### Validation Error Response

```typescript
{
  code: "validation_error";
  message: string;
  errors?: Array<{
    field: string;     // Field name
    message: string;   // Error message
  }>;
}
```

## Security Considerations

1. **HTTPS Only**: All API requests must use HTTPS in production
2. **Token Storage**: Store tokens securely (never in localStorage for sensitive apps)
3. **Token Refresh**: Implement automatic token refresh in clients
4. **Password Requirements**: Enforce strong passwords (8+ chars, mixed case, numbers, symbols)
5. **Rate Limiting**: Implement exponential backoff on rate limit errors
6. **CORS**: Configure appropriate CORS headers for your domain

## SDK Support

Official SDKs are available for:
- **Python**: `pip install fullstack-api-client`
- **TypeScript/JavaScript**: `npm install @fullstack/api-client`

See the respective SDK documentation for usage examples and best practices.

## Webhooks

The API supports webhooks for the following events:
- `user.created`: New user registration
- `user.updated`: User profile update
- `user.deleted`: User account deletion
- `auth.login`: Successful login
- `auth.logout`: User logout

Configure webhooks in your account settings.

## API Versioning

The API uses URL versioning. The current version is `v1`. Future versions will be available at `/api/v2/`, etc.

We'll maintain backward compatibility within major versions and provide migration guides for breaking changes.

## Support

- **Documentation**: https://docs.example.com
- **Status Page**: https://status.example.com
- **Support Email**: support@example.com
- **GitHub Issues**: https://github.com/yourusername/fullstack-api/issues