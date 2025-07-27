"""Custom exceptions."""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 401, details)


class AuthorizationError(AppException):
    """Authorization error."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 403, details)


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 400, details)


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 404, details)


class ConflictError(AppException):
    """Resource conflict error."""

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 409, details)


class RateLimitError(AppException):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 429, details)


class TokenError(AppException):
    """Token error."""

    def __init__(
        self,
        message: str = "Invalid token",
        code: str = "TOKEN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 401, details)


class DatabaseError(AppException):
    """Database error."""

    def __init__(
        self,
        message: str = "Database error occurred",
        code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, 500, details)
