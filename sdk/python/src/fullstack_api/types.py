"""Type definitions for FullStack API Client."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class AuthTokens:
    """Authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class LoginRequest:
    """Login request data."""
    username: str
    password: str


@dataclass
class RegisterRequest:
    """Registration request data."""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


@dataclass
class User:
    """User model."""
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    full_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create User from dictionary."""
        return cls(
            id=data["id"],
            email=data["email"],
            username=data["username"],
            full_name=data.get("full_name"),
            is_active=data["is_active"],
            is_verified=data["is_verified"],
            is_superuser=data["is_superuser"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class UpdateUserRequest:
    """Update user request data."""
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ChangePasswordRequest:
    """Change password request data."""
    old_password: str
    new_password: str


@dataclass
class PasswordResetRequest:
    """Password reset request data."""
    email: str


@dataclass
class PasswordResetConfirm:
    """Password reset confirmation data."""
    token: str
    new_password: str


@dataclass
class HealthCheck:
    """Health check response."""
    status: str
    database: str
    version: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthCheck":
        """Create HealthCheck from dictionary."""
        return cls(
            status=data["status"],
            database=data["database"],
            version=data["version"],
        )