"""API dependencies."""

from typing import Annotated, Optional, Dict, Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import TokenPayload
from app.core.cache import cache_user
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import get_db

# Security scheme
security = HTTPBearer()


async def get_current_user_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenPayload:
    """Get current user from JWT token."""
    token = credentials.credentials

    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise AuthenticationError(
            message="Invalid authentication credentials",
            code="INVALID_TOKEN",
        )

    # Check token type
    if token_data.type != "access":
        raise AuthenticationError(
            message="Invalid token type",
            code="INVALID_TOKEN_TYPE",
        )

    return token_data


# Type annotation for the decorator is complex, using Any to satisfy mypy
@cache_user(ttl=300)  # type: ignore[misc]
async def get_user_by_id(
    user_id: str,
    db: AsyncSession,
) -> Optional[User]:
    """Get user by ID from database."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_current_user(
    token_data: Annotated[TokenPayload, Depends(get_current_user_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user."""
    user = await get_user_by_id(token_data.sub, db)

    if not user:
        raise AuthenticationError(
            message="User not found",
            code="USER_NOT_FOUND",
        )

    if not user.is_active:
        raise AuthenticationError(
            message="User is inactive",
            code="USER_INACTIVE",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationError(
            message="Inactive user",
            code="USER_INACTIVE",
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise AuthorizationError(
            message="Email not verified",
            code="EMAIL_NOT_VERIFIED",
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise AuthorizationError(
            message="Not enough permissions",
            code="INSUFFICIENT_PERMISSIONS",
        )
    return current_user


# Optional authentication
async def get_optional_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return None

        payload = decode_token(token)
        token_data = TokenPayload(**payload)

        if token_data.type != "access":
            return None

        user = await get_user_by_id(token_data.sub, db)
        if user and user.is_active:
            return user
    except Exception:
        pass

    return None


# Pagination dependencies
def get_pagination_params(
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, int]:
    """Get pagination parameters."""
    return {
        "page": max(1, page),
        "per_page": min(max(1, per_page), 100),
    }
