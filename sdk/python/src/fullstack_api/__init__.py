"""FullStack API Python Client Library."""

from .client import FullStackClient
from .exceptions import (
    FullStackAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    ServerError,
)
from .storage import TokenStorage, MemoryTokenStorage, FileTokenStorage
from .types import (
    AuthTokens,
    User,
    LoginRequest,
    RegisterRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    HealthCheck,
)

__version__ = "1.0.0"
__all__ = [
    "FullStackClient",
    "FullStackAPIError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NotFoundError",
    "ServerError",
    "TokenStorage",
    "MemoryTokenStorage",
    "FileTokenStorage",
    "AuthTokens",
    "User",
    "LoginRequest",
    "RegisterRequest",
    "UpdateUserRequest",
    "ChangePasswordRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "HealthCheck",
]