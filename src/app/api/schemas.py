"""API schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.utils import validate_password, validate_username


# Base schemas
class BaseResponse(BaseModel):
    """Base response model."""

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )


class SuccessResponse(BaseModel):
    """Success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Response data"
    )


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, errors = validate_password(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Validate username format."""
        is_valid, error = validate_username(v)
        if not is_valid:
            raise ValueError(error)
        return v


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is None:
            return v
        is_valid, error = validate_username(v)
        if not is_valid:
            raise ValueError(error)
        return v


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    # v1.1+ fields (example for future use)
    # preferences: Optional[Dict[str, Any]] = None
    # profile_picture_url: Optional[str] = None

    # v1.2+ fields (example for future use)
    # two_factor_enabled: Optional[bool] = None
    # last_password_change: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_versioned(
        cls, obj: Any, version: str = "1.0"
    ) -> "UserResponse":
        """Create versioned response based on API version."""
        # Base fields for all versions
        data = {
            "id": obj.id,
            "email": obj.email,
            "username": obj.username,
            "is_active": obj.is_active,
            "is_verified": obj.is_verified,
            "is_superuser": obj.is_superuser,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
            "last_login_at": obj.last_login_at,
        }

        # Add version-specific fields
        # if version >= "1.1":
        #     data["preferences"] = obj.preferences
        #     data["profile_picture_url"] = obj.profile_picture_url

        # if version >= "1.2":
        #     data["two_factor_enabled"] = obj.two_factor_enabled
        #     data["last_password_change"] = obj.last_password_change

        return cls(**data)


class UserInDB(UserResponse):
    """User in database schema."""

    hashed_password: str


# Auth schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RegisterRequest(UserCreate):
    """Register request schema."""

    pass


class RegisterResponse(BaseModel):
    """Register response schema."""

    message: str = "User registered successfully"
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str
    exp: datetime
    iat: datetime
    type: str


# Password schemas
class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, errors = validate_password(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, errors = validate_password(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response schema."""

    items: list[Any]
    total: int
    page: int
    per_page: int
    pages: int
