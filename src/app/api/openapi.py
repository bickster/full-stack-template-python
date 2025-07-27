"""OpenAPI documentation configuration."""

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="""
## FullStack Application API

This is the REST API for the FullStack application template.

### Features:
- JWT-based authentication with refresh tokens
- User registration and management
- Password reset functionality
- Rate limiting on authentication endpoints
- Comprehensive error handling
- Health monitoring endpoints

### Authentication:
This API uses JWT tokens for authentication. To access protected endpoints:

1. Register a new user or login with existing credentials
2. Use the access token in the Authorization header: `Bearer <token>`
3. Refresh the token before it expires using the refresh endpoint

### Rate Limiting:
Authentication endpoints are rate-limited to prevent abuse:
- Login: 5 attempts per 15 minutes
- Registration: 5 attempts per hour
- Password reset: 3 attempts per hour

### Error Responses:
All endpoints follow a consistent error response format:
```json
{
    "error": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

### Versioning:
The API is versioned through the URL path. Current version: v1
""",
        routes=app.routes,
        tags=[
            {
                "name": "Authentication",
                "description": "User authentication endpoints",
            },
            {
                "name": "Users",
                "description": "User management endpoints",
            },
            {
                "name": "Health",
                "description": "Application health monitoring",
            },
        ],
        servers=[
            {
                "url": f"https://api.{settings.DOMAIN}",
                "description": "Production server",
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server",
            },
        ],
        contact={
            "name": "API Support",
            "email": settings.CONTACT_EMAIL,
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token authentication",
        }
    }

    # Add example schemas
    openapi_schema["components"]["examples"] = {
        "LoginExample": {
            "summary": "Example login request",
            "value": {
                "username": "john_doe",
                "password": "SecurePassword123!",
            },
        },
        "RegisterExample": {
            "summary": "Example registration request",
            "value": {
                "email": "john@example.com",
                "username": "john_doe",
                "password": "SecurePassword123!",
                "full_name": "John Doe",
            },
        },
        "TokenExample": {
            "summary": "Example token response",
            "value": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            },
        },
    }

    # Add common responses
    openapi_schema["components"]["responses"] = {
        "UnauthorizedError": {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "code": {"type": "string"},
                        },
                    },
                    "example": {
                        "error": "Invalid credentials",
                        "code": "INVALID_CREDENTIALS",
                    },
                }
            },
        },
        "ValidationError": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "code": {"type": "string"},
                            "details": {
                                "type": "object",
                                "properties": {
                                    "errors": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "field": {"type": "string"},
                                                "message": {"type": "string"},
                                                "type": {"type": "string"},
                                            },
                                        },
                                    }
                                },
                            },
                        },
                    }
                }
            },
        },
        "RateLimitError": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "code": {"type": "string"},
                            "retry_after": {"type": "integer"},
                        },
                    },
                    "example": {
                        "error": "Too many login attempts",
                        "code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": 900,
                    },
                }
            },
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
