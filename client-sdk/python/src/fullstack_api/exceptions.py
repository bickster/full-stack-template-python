"""Exception classes for the Full-Stack API SDK."""

from typing import Any, Dict, Optional


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize API error."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        """String representation."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        """Initialize authentication error."""
        super().__init__(
            message, status_code=401, code="authentication_error", **kwargs
        )


class ValidationError(APIError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[list] = None,
        **kwargs,
    ):
        """Initialize validation error."""
        super().__init__(message, status_code=422, code="validation_error", **kwargs)
        self.errors = errors or []


class NotFoundError(APIError):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        """Initialize not found error."""
        super().__init__(message, status_code=404, code="not_found", **kwargs)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        """Initialize rate limit error."""
        super().__init__(message, status_code=429, code="rate_limit_exceeded", **kwargs)
        self.retry_after = retry_after


class ServerError(APIError):
    """Raised when server encounters an error."""

    def __init__(self, message: str = "Internal server error", **kwargs):
        """Initialize server error."""
        super().__init__(message, status_code=500, code="server_error", **kwargs)
