"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.db.models.user import User


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints."""

    async def test_register_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPass123!",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert "id" in data["user"]

        # Verify user in database
        user = await db_session.get(User, data["user"]["id"])
        assert user is not None
        assert user.email == "newuser@example.com"
        assert verify_password("NewPass123!", user.hashed_password)

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "NewPass123!",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "Email already registered"
        assert data["code"] == "EMAIL_EXISTS"

    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "password": "NewPass123!",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "Username already taken"
        assert data["code"] == "USERNAME_EXISTS"

    async def test_register_invalid_data(self, client: AsyncClient):
        """Test registration with invalid data."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "u",  # Too short
                "password": "weak",  # Too weak
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "details" in data

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
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
        assert data["expires_in"] == 900  # 15 minutes
        assert data["user"]["id"] == str(test_user.id)
        assert data["user"]["email"] == test_user.email

    async def test_login_invalid_password(
        self, client: AsyncClient, test_user: User
    ):
        """Test login with invalid password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Invalid email or password"
        assert data["code"] == "INVALID_CREDENTIALS"

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Invalid email or password"
        assert data["code"] == "INVALID_CREDENTIALS"

    async def test_login_inactive_user(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test login with inactive user."""
        # Make user inactive
        test_user.is_active = False
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "User account is inactive"
        assert data["code"] == "USER_INACTIVE"

    async def test_refresh_token_success(
        self, client: AsyncClient, test_user: User
    ):
        """Test successful token refresh."""
        # First login to get tokens
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
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Invalid refresh token"
        assert data["code"] == "INVALID_REFRESH_TOKEN"

    async def test_logout_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    async def test_logout_unauthorized(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 403  # No auth header provided
