"""Authentication endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    SuccessResponse,
    UserResponse,
)
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    RateLimitError,
)
from app.core.logging import logger
from app.core.monitoring import record_login_attempt, record_token_operation
from app.core.rate_limit import login_rate_limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.utils import get_client_ip, get_user_agent
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == register_data.email)
    )
    if result.scalar_one_or_none():
        raise ConflictError(
            message="Email already registered",
            code="EMAIL_EXISTS",
        )

    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == register_data.username)
    )
    if result.scalar_one_or_none():
        raise ConflictError(
            message="Username already taken",
            code="USERNAME_EXISTS",
        )

    # Create new user
    user = User(
        email=register_data.email,
        username=register_data.username,
        hashed_password=get_password_hash(register_data.password),
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(
        "user_registered",
        user_id=str(user.id),
        email=user.email,
        username=user.username,
    )

    return RegisterResponse(
        message="User registered successfully",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Login user and return access/refresh tokens."""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Check rate limit
    is_allowed, remaining, retry_after = (
        await login_rate_limiter.check_login_rate_limit(
            db, login_data.email, ip_address
        )
    )

    if not is_allowed:
        await login_rate_limiter.record_login_attempt(
            db, login_data.email, ip_address, False, user_agent=user_agent
        )
        raise RateLimitError(
            message="Too many login attempts. Please try again later.",
            details={
                "retry_after": (
                    retry_after.isoformat() if retry_after else None
                ),
            },
        )

    # Find user by email
    result = await db.execute(
        select(User).where(
            User.email == login_data.email,
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()

    # Verify user and password
    if not user or not verify_password(
        login_data.password, user.hashed_password
    ):
        # Record failed attempt
        await login_rate_limiter.record_login_attempt(
            db, login_data.email, ip_address, False, user_agent=user_agent
        )
        record_login_attempt(success=False)

        raise AuthenticationError(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
        )

    # Check if user is active
    if not user.is_active:
        raise AuthenticationError(
            message="User account is inactive",
            code="USER_INACTIVE",
        )

    # Record successful login
    await login_rate_limiter.record_login_attempt(
        db, login_data.email, ip_address, True, str(user.id), user_agent
    )
    record_login_attempt(success=True)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # Store refresh token
    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token_obj)

    await db.commit()
    await db.refresh(user)

    # Record token operations
    record_token_operation("create", "access")
    record_token_operation("create", "refresh")

    logger.info(
        "user_login",
        user_id=str(user.id),
        email=user.email,
        ip_address=ip_address,
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

    except Exception:
        raise AuthenticationError(
            message="Invalid refresh token",
            code="INVALID_REFRESH_TOKEN",
        )

    # Find all refresh tokens for this user
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    refresh_tokens = result.scalars().all()

    # Verify refresh token exists and is valid
    token_valid = False
    for token in refresh_tokens:
        if verify_password(refresh_data.refresh_token, token.token_hash):
            if token.is_valid:
                token_valid = True
            break

    if not token_valid:
        raise AuthenticationError(
            message="Invalid or expired refresh token",
            code="INVALID_REFRESH_TOKEN",
        )

    # Get user
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError(
            message="User not found or inactive",
            code="USER_NOT_FOUND",
        )

    # Create new access token
    access_token = create_access_token(subject=str(user.id))

    record_token_operation("refresh", "access")

    logger.info(
        "token_refreshed",
        user_id=str(user.id),
        email=user.email,
    )

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse:
    """Logout user by revoking refresh tokens."""
    # Revoke all refresh tokens for this user
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
        "user_logout",
        user_id=str(current_user.id),
        email=current_user.email,
        tokens_revoked=len(refresh_tokens),
    )

    return SuccessResponse(
        message="Logged out successfully",
    )
