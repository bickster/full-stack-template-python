"""Unit tests for security functions."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_get_password_hash(self):
        """Test password hash generation."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different even for same password
        assert hash1 != hash2
        # Hash should be bcrypt format
        assert hash1.startswith("$2b$")
        assert len(hash1) == 60

    def test_verify_password(self):
        """Test password verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True
        # Wrong password should not verify
        assert verify_password(wrong_password, hashed) is False
        # Empty password should not verify
        assert verify_password("", hashed) is False


class TestTokenCreation:
    """Test JWT token creation."""

    def test_create_access_token(self):
        """Test access token creation."""
        subject = "test-user-id"
        token = create_access_token(subject)

        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == subject
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

        # Check expiration time (15 minutes)
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - iat_time).total_seconds() == pytest.approx(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, rel=1
        )

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        subject = "test-user-id"
        expires_delta = timedelta(hours=1)
        token = create_access_token(subject, expires_delta)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - iat_time).total_seconds() == pytest.approx(
            3600, rel=1
        )

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        subject = "test-user-id"
        token = create_refresh_token(subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == subject
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

        # Check expiration time (30 days)
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - iat_time).total_seconds() == pytest.approx(
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, rel=1
        )

    def test_create_refresh_token_with_custom_expiry(self):
        """Test refresh token creation with custom expiry."""
        subject = "test-user-id"
        custom_delta = timedelta(days=7)
        token = create_refresh_token(
            subject=subject, expires_delta=custom_delta
        )

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == subject
        assert payload["type"] == "refresh"

        # Check custom expiration time (7 days)
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - iat_time).total_seconds() == pytest.approx(
            7 * 24 * 60 * 60, rel=1
        )


class TestTokenDecoding:
    """Test JWT token decoding."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        subject = "test-user-id"
        token = create_access_token(subject)

        payload = decode_token(token)

        assert payload["sub"] == subject
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("invalid.token.here")

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        subject = "test-user-id"
        # Create token that expires immediately
        token = create_access_token(subject, timedelta(seconds=-1))

        with pytest.raises(ValueError, match="Invalid token"):
            decode_token(token)

    def test_decode_token_with_wrong_secret(self):
        """Test decoding token with wrong secret."""
        subject = "test-user-id"
        # Create token with different secret
        to_encode = {
            "sub": subject,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = jwt.encode(
            to_encode, "wrong-secret", algorithm=settings.ALGORITHM
        )

        with pytest.raises(ValueError, match="Invalid token"):
            decode_token(token)
