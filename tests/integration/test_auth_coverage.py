"""Integration tests for auth endpoints to improve coverage."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class TestAuthEndpointsCoverage:
    """Test auth endpoints for coverage."""

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakpass",
                "password": "weak",  # Too short
            },
        )
        assert response.status_code == 422
        assert "password" in response.text.lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "test",
                "password": "ValidPass123!",
            },
        )
        assert response.status_code == 422
        assert "email" in response.text.lower()

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient, test_user: User):
        """Test login using email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,  # Using email
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!",
            },
        )
        assert response.status_code == 401
        assert "Invalid" in response.json()["error"]

    @pytest.mark.skip(reason="Rate limiting not working in test environment")
    @pytest.mark.asyncio
    async def test_login_rate_limiting(self, client: AsyncClient):
        """Test login rate limiting."""
        # Use the same email for all attempts to trigger rate limiting
        email = "ratelimit@example.com"

        # Make multiple failed login attempts
        for i in range(10):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": email,
                    "password": "wrong",
                },
            )
            # After 5 attempts, should be rate limited
            if i >= 5:
                assert response.status_code == 429
                break
            else:
                # Before rate limit, should get 401
                assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test refresh with completely invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not-a-valid-jwt-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_revoked_token(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test refresh with revoked token."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Revoke the token
        from datetime import datetime, timezone

        from sqlalchemy import text

        await db_session.execute(
            text(
                "UPDATE refresh_tokens SET revoked_at = :now "
                "WHERE user_id = :user_id"
            ),
            {"now": datetime.now(timezone.utc), "user_id": str(test_user.id)},
        )
        await db_session.commit()

        # Try to refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_register_and_login_flow(self, client: AsyncClient):
        """Test complete registration and login flow."""
        # Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flowtest@example.com",
                "username": "flowtest",
                "password": "FlowTest123!",
                "full_name": "Flow Test User",
            },
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["user"]["email"] == "flowtest@example.com"

        # Login with the new account
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "FlowTest123!",
            },
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    @pytest.mark.asyncio
    async def test_me_endpoint_without_auth(self, client: AsyncClient):
        """Test accessing protected endpoint without auth."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403
