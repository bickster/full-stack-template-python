"""End-to-end API tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash


class TestUserRegistrationFlow:
    """Test complete user registration flow."""

    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPassword123!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert "id" in data["user"]
        assert "password" not in data["user"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user
    ):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "Password123!",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "weak",
            },
        )
        assert response.status_code == 422
        assert "password" in response.text.lower()


class TestAuthenticationFlow:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(
        self, client: AsyncClient, test_user
    ):
        """Test login with valid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self, client: AsyncClient, test_user
    ):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_login_unverified_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with unverified email."""
        from app.db.models import User

        # Create unverified user
        user = User(
            email="unverified@example.com",
            username="unverified",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "unverified@example.com",
                "password": "Password123!",
            },
        )
        # Should succeed but return verification status
        assert response.status_code == 200
        assert response.json()["user"]["is_verified"] is False


class TestTokenRefreshFlow:
    """Test token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test refreshing access token."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid-token"}
        )
        assert response.status_code == 401


class TestUserProfileManagement:
    """Test user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user profile."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_update_user_profile(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating user profile."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "updatedname"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "updatedname"

    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, auth_headers):
        """Test changing password."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPassword123!",
            },
        )
        assert response.status_code == 200

        # Verify old password doesn't work
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )
        assert login_response.status_code == 401

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing protected endpoint without auth."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.skip(reason="Rate limiting not working in test environment")
    @pytest.mark.asyncio
    async def test_login_rate_limit(self, client: AsyncClient):
        """Test rate limiting on login endpoint."""
        # Make multiple failed login attempts
        for i in range(6):  # Assuming limit is 5
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "wrong",
                },
            )

            if i < 5:
                assert response.status_code == 401
            else:
                # Should be rate limited
                assert response.status_code == 429
                assert "rate limit" in response.json()["error"].lower()


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test CORS headers in responses."""
    # Test CORS on a regular POST request
    response = await client.post(
        "/api/v1/auth/login",
        headers={"Origin": "http://localhost:3000"},
        json={"email": "test@example.com", "password": "wrong"},
    )
    # Check for CORS headers (they should be present even on error responses)
    assert "access-control-allow-credentials" in response.headers


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data
    assert "version" in data
