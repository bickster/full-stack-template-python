"""FullStack API Python Client Library."""

from .client import FullStackClient
from .exceptions import (
    AuthenticationError,
    FullStackAPIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .storage import FileTokenStorage, MemoryTokenStorage, TokenStorage
from .types import (
    AuthTokens,
    ChangePasswordRequest,
    HealthCheck,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    UpdateUserRequest,
    User,
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
