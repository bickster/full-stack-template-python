"""Integration tests for user endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.db.models.user import User


@pytest.mark.asyncio
class TestUserEndpoints:
    """Test user management endpoints."""

    async def test_get_current_user(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test getting current user profile."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["is_active"] is True
        assert data["is_verified"] is True

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403

    async def test_update_user_email(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test updating user email."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "newemail@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
        assert data["is_verified"] is False  # Email change resets verification

    async def test_update_user_username(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test updating username."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "newusername"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"

    async def test_update_user_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User,
        test_superuser: User,
        auth_headers: dict,
    ):
        """Test updating to duplicate email."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": test_superuser.email},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "Email already registered"
        assert data["code"] == "EMAIL_EXISTS"

    async def test_update_user_invalid_data(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test updating with invalid data."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "a"},  # Too short
        )

        assert response.status_code == 422

    async def test_change_password_success(
        self,
        client: AsyncClient,
        async_session: AsyncSession,
        test_user: User,
        auth_headers: dict,
    ):
        """Test successful password change."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"

        # Verify password was changed
        await async_session.refresh(test_user)
        assert verify_password("NewPass123!", test_user.hashed_password)

    async def test_change_password_wrong_current(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test changing password with wrong current password."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPass123!",
                "new_password": "NewPass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Current password is incorrect"
        assert data["code"] == "INVALID_PASSWORD"

    async def test_change_password_same_password(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test changing to same password."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "TestPass123!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == (
            "New password must be different from current password"
        )
        assert data["code"] == "SAME_PASSWORD"

    async def test_delete_account_success(
        self,
        client: AsyncClient,
        async_session: AsyncSession,
        test_user: User,
        auth_headers: dict,
    ):
        """Test successful account deletion."""
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User account deleted successfully"

        # Verify user is soft deleted
        await async_session.refresh(test_user)
        assert test_user.deleted_at is not None
        assert test_user.is_active is False

    async def test_delete_account_unverified_user(
        self,
        client: AsyncClient,
        async_session: AsyncSession,
        test_user: User,
        auth_headers: dict,
    ):
        """Test account deletion requires verified email."""
        # Make user unverified
        test_user.is_verified = False
        await async_session.commit()

        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "Email not verified"
        assert data["code"] == "EMAIL_NOT_VERIFIED"
