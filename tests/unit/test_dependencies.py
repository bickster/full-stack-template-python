"""Unit tests for API dependencies."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_user, get_current_user_token
from app.api.schemas import TokenPayload
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.db.models.user import User


class TestGetCurrentUserToken:
    """Test get_current_user_token dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_token_valid(self):
        """Test getting user token with valid credentials."""
        # Create valid token
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)

        # Mock credentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Call dependency
        token_payload = await get_current_user_token(credentials)

        assert isinstance(token_payload, TokenPayload)
        assert token_payload.sub == user_id
        assert token_payload.type == "access"

    @pytest.mark.asyncio
    async def test_get_current_user_token_invalid(self):
        """Test getting user token with invalid credentials."""
        # Mock invalid credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            await get_current_user_token(credentials)

    @pytest.mark.asyncio
    async def test_get_current_user_token_expired(self):
        """Test getting user token with expired token."""
        from datetime import timedelta

        # Create expired token
        user_id = "test-user-id"
        token = create_access_token(
            subject=user_id, expires_delta=timedelta(seconds=-1)
        )

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            await get_current_user_token(credentials)


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    @pytest.mark.asyncio
    @patch("app.api.dependencies.get_user_by_id")
    async def test_get_current_user_valid(self, mock_get_user_by_id):
        """Test getting current user with valid token."""
        # Mock user
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        from datetime import datetime, timedelta, timezone

        # Mock token payload with required fields
        now = datetime.now(timezone.utc)
        token_payload = TokenPayload(
            sub="test-user-id",
            type="access",
            exp=now + timedelta(minutes=15),
            iat=now,
        )

        # Mock get_user_by_id to return user
        mock_get_user_by_id.return_value = mock_user

        # Mock database session
        mock_db = AsyncMock()

        # Call dependency
        user = await get_current_user(token_data=token_payload, db=mock_db)

        assert user == mock_user
        assert user.id == "test-user-id"
        assert user.email == "test@example.com"
        mock_get_user_by_id.assert_called_once_with("test-user-id", mock_db)

    @pytest.mark.asyncio
    @patch("app.api.dependencies.get_user_by_id")
    async def test_get_current_user_not_found(self, mock_get_user_by_id):
        """Test getting current user when user not found."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        token_payload = TokenPayload(
            sub="nonexistent-user-id",
            type="access",
            exp=now + timedelta(minutes=15),
            iat=now,
        )

        # Mock get_user_by_id to return None
        mock_get_user_by_id.return_value = None

        # Mock database session
        mock_db = AsyncMock()

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError, match="User not found"):
            await get_current_user(token_data=token_payload, db=mock_db)

    @pytest.mark.asyncio
    @patch("app.api.dependencies.get_user_by_id")
    async def test_get_current_user_inactive(self, mock_get_user_by_id):
        """Test getting current user when user is inactive."""
        # Mock inactive user
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=False,
        )

        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        token_payload = TokenPayload(
            sub="test-user-id",
            type="access",
            exp=now + timedelta(minutes=15),
            iat=now,
        )

        # Mock get_user_by_id to return inactive user
        mock_get_user_by_id.return_value = mock_user

        # Mock database session
        mock_db = AsyncMock()

        # Should raise AuthenticationError (check correct message)
        with pytest.raises(AuthenticationError, match="User is inactive"):
            await get_current_user(token_data=token_payload, db=mock_db)
