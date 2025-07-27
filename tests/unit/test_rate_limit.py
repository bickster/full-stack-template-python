"""Unit tests for rate limiting."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.rate_limit import LoginRateLimiter
from app.db.models import LoginAttempt


class TestLoginRateLimiter:
    """Test login rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_check_login_rate_limit_no_attempts(self):
        """Test rate limit check with no previous attempts."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()

        # Mock no previous attempts
        mock_result = Mock()
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        result = await limiter.check_login_rate_limit(
            mock_db, "test@example.com", "127.0.0.1"
        )
        is_allowed, remaining, retry_after = result

        assert is_allowed is True
        assert remaining == 15
        assert retry_after is None

    @pytest.mark.asyncio
    async def test_check_login_rate_limit_under_limit(self):
        """Test rate limit check with attempts under limit."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()

        # Mock 3 previous attempts (under limit of 15)
        mock_result = Mock()
        mock_result.scalar.return_value = 3
        mock_db.execute.return_value = mock_result

        result = await limiter.check_login_rate_limit(
            mock_db, "test@example.com", "127.0.0.1"
        )
        is_allowed, remaining, retry_after = result

        assert is_allowed is True
        assert remaining == 12
        assert retry_after is None

    @pytest.mark.asyncio
    async def test_check_login_rate_limit_at_limit(self):
        """Test rate limit check at the limit."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()

        # Mock 15 previous attempts (at limit)
        mock_result = Mock()
        mock_result.scalar.return_value = 15

        # Mock the second query for oldest attempt time
        oldest_attempt_time = datetime.now(timezone.utc) - timedelta(
            minutes=10
        )
        mock_oldest_result = Mock()
        mock_oldest_result.scalar.return_value = oldest_attempt_time

        # Set up execute to return different results for each call
        mock_db.execute = AsyncMock(
            side_effect=[mock_result, mock_oldest_result]
        )

        result = await limiter.check_login_rate_limit(
            mock_db, "test@example.com", "127.0.0.1"
        )
        is_allowed, remaining, retry_after = result

        assert is_allowed is False
        assert remaining == 0
        assert retry_after is not None
        assert isinstance(retry_after, datetime)

    @pytest.mark.asyncio
    async def test_check_login_rate_limit_over_limit(self):
        """Test rate limit check over the limit."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()

        # Mock 20 previous attempts (well over limit)
        mock_result = Mock()
        mock_result.scalar.return_value = 20

        # Mock the second query for oldest attempt time
        oldest_attempt_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        mock_oldest_result = Mock()
        mock_oldest_result.scalar.return_value = oldest_attempt_time

        # Set up execute to return different results for each call
        mock_db.execute = AsyncMock(
            side_effect=[mock_result, mock_oldest_result]
        )

        result = await limiter.check_login_rate_limit(
            mock_db, "test@example.com", "127.0.0.1"
        )
        is_allowed, remaining, retry_after = result

        assert is_allowed is False
        assert remaining == 0
        assert retry_after is not None

    @pytest.mark.asyncio
    async def test_record_login_attempt_success(self):
        """Test recording successful login attempt."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()

        await limiter.record_login_attempt(
            mock_db,
            email="test@example.com",
            ip_address="127.0.0.1",
            user_agent="Test Browser",
            success=True,
            user_id="user-123",
        )

        # Verify attempt was added
        mock_db.add.assert_called_once()
        added_attempt = mock_db.add.call_args[0][0]
        assert isinstance(added_attempt, LoginAttempt)
        assert added_attempt.email == "test@example.com"
        assert added_attempt.ip_address == "127.0.0.1"
        assert added_attempt.user_agent == "Test Browser"
        assert added_attempt.success is True
        assert added_attempt.user_id == "user-123"

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_login_attempt_failure(self):
        """Test recording failed login attempt."""
        limiter = LoginRateLimiter()
        mock_db = AsyncMock()
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()

        await limiter.record_login_attempt(
            mock_db,
            email="test@example.com",
            ip_address="127.0.0.1",
            user_agent="Test Browser",
            success=False,
            user_id=None,
        )

        # Verify attempt was added
        mock_db.add.assert_called_once()
        added_attempt = mock_db.add.call_args[0][0]
        assert added_attempt.success is False
        assert added_attempt.user_id is None

        mock_db.commit.assert_called_once()

    def test_login_rate_limiter_custom_settings(self):
        """Test login rate limiter with custom settings."""
        limiter = LoginRateLimiter(max_attempts=10, window_minutes=30)
        assert limiter.max_attempts == 10
        assert limiter.window_minutes == 30
