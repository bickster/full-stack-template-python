"""Exceptions for FullStack API Client."""

from typing import Optional, Dict, Any


class FullStackAPIError(Exception):
    """Base exception for FullStack API errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ):
        """Initialize exception."""
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code


class AuthenticationError(FullStackAPIError):
    """Authentication failed."""
    pass


class ValidationError(FullStackAPIError):
    """Validation error."""
    
    @property
    def errors(self) -> list:
        """Get validation errors."""
        return self.details.get("errors", [])


class RateLimitError(FullStackAPIError):
    """Rate limit exceeded."""
    
    @property
    def retry_after(self) -> Optional[int]:
        """Get retry after time in seconds."""
        return self.details.get("retry_after")


class NotFoundError(FullStackAPIError):
    """Resource not found."""
    pass


class ServerError(FullStackAPIError):
    """Server error."""
    pass