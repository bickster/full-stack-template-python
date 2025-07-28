"""Unit tests for database models."""

from datetime import datetime, timedelta, timezone

from app.db.models import AuditLog, LoginAttempt, RefreshToken, User


class TestUserModel:
    """Test User model properties."""

    def test_user_repr(self):
        """Test User string representation."""
        user = User(id="user-123", email="test@example.com", username="testuser")
        assert repr(user) == "<User testuser>"

    def test_user_is_deleted(self):
        """Test User is_deleted property."""
        user = User(deleted_at=datetime.now(timezone.utc))
        assert user.is_deleted is True

        active_user = User(deleted_at=None)
        assert active_user.is_deleted is False


class TestRefreshTokenModel:
    """Test RefreshToken model properties."""

    def test_refresh_token_repr(self):
        """Test RefreshToken string representation."""
        token = RefreshToken(id="token-123")
        assert repr(token) == "<RefreshToken token-123>"

    def test_refresh_token_is_expired(self):
        """Test RefreshToken is_expired property."""
        # Expired token
        expired_token = RefreshToken(
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        assert expired_token.is_expired is True

        # Valid token
        valid_token = RefreshToken(
            expires_at=datetime.now(timezone.utc) + timedelta(days=1)
        )
        assert valid_token.is_expired is False

    def test_refresh_token_is_revoked(self):
        """Test RefreshToken is_revoked property."""
        # Revoked token
        revoked_token = RefreshToken(revoked_at=datetime.now(timezone.utc))
        assert revoked_token.is_revoked is True

        # Active token
        active_token = RefreshToken(revoked_at=None)
        assert active_token.is_revoked is False

    def test_refresh_token_is_valid(self):
        """Test RefreshToken is_valid property."""
        # Valid token
        valid_token = RefreshToken(
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked_at=None,
        )
        assert valid_token.is_valid is True

        # Expired token
        expired_token = RefreshToken(
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            revoked_at=None,
        )
        assert expired_token.is_valid is False

        # Revoked token
        revoked_token = RefreshToken(
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked_at=datetime.now(timezone.utc),
        )
        assert revoked_token.is_valid is False


class TestLoginAttemptModel:
    """Test LoginAttempt model properties."""

    def test_login_attempt_repr(self):
        """Test LoginAttempt string representation."""
        attempt = LoginAttempt(id="attempt-123", email="test@example.com", success=True)
        assert repr(attempt) == "<LoginAttempt test@example.com - Success>"

        failed_attempt = LoginAttempt(
            id="attempt-123", email="test@example.com", success=False
        )
        assert repr(failed_attempt) == ("<LoginAttempt test@example.com - Failed>")


class TestAuditLogModel:
    """Test AuditLog model properties."""

    def test_audit_log_repr(self):
        """Test AuditLog string representation."""
        log = AuditLog(id="log-123", action="user.login", user_id="user-456")
        assert repr(log) == "<AuditLog user.login by user-456>"
