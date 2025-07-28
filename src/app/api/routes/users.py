"""User management endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_current_verified_user
from app.api.middleware import get_api_version
from app.api.schemas import (
    PasswordChangeRequest,
    SuccessResponse,
    UserResponse,
    UserUpdate,
)
from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user profile."""
    # Get API version from request
    version = get_api_version(request)

    # Return versioned response
    return UserResponse.from_orm_versioned(current_user, version)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: Request,
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update current user profile."""
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        return UserResponse.model_validate(current_user)

    # Check if email is being updated and already exists
    if "email" in update_data and update_data["email"] != current_user.email:
        result = await db.execute(
            select(User).where(
                User.email == update_data["email"],
                User.id != current_user.id,
            )
        )
        if result.scalar_one_or_none():
            raise ConflictError(
                message="Email already registered",
                code="EMAIL_EXISTS",
            )

        # Mark email as unverified when changed
        current_user.is_verified = False

    # Check if username is being updated and already exists
    if "username" in update_data and update_data["username"] != current_user.username:
        result = await db.execute(
            select(User).where(
                User.username == update_data["username"],
                User.id != current_user.id,
            )
        )
        if result.scalar_one_or_none():
            raise ConflictError(
                message="Username already taken",
                code="USERNAME_EXISTS",
            )

    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(current_user)

    logger.info(
        "user_updated",
        user_id=str(current_user.id),
        updated_fields=list(update_data.keys()),
    )

    # Get API version and return versioned response
    version = get_api_version(request)
    return UserResponse.from_orm_versioned(current_user, version)


@router.post("/me/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse:
    """Change current user password."""
    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise AuthenticationError(
            message="Current password is incorrect",
            code="INVALID_PASSWORD",
        )

    # Check if new password is different
    if password_data.current_password == password_data.new_password:
        raise ValidationError(
            message="New password must be different from current password",
            code="SAME_PASSWORD",
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        "password_changed",
        user_id=str(current_user.id),
        email=current_user.email,
    )

    return SuccessResponse(
        message="Password changed successfully",
    )


@router.delete("/me", response_model=SuccessResponse)
async def delete_current_user(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse:
    """Delete current user account (soft delete)."""
    # Soft delete the user
    current_user.deleted_at = datetime.now(timezone.utc)
    current_user.is_active = False

    # Revoke all refresh tokens
    from app.db.models.refresh_token import RefreshToken

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    refresh_tokens = result.scalars().all()

    for token in refresh_tokens:
        token.revoked_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        "user_deleted",
        user_id=str(current_user.id),
        email=current_user.email,
    )

    return SuccessResponse(
        message="User account deleted successfully",
    )
