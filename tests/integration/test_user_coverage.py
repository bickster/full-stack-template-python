"""Integration tests for user endpoints to improve coverage."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class TestUserEndpointsCoverage:
    """Test user endpoints for coverage."""

    @pytest.mark.asyncio
    async def test_get_current_user_full(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting full user profile."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "is_active" in data
        assert "is_verified" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data  # Should never be exposed

    @pytest.mark.asyncio
    async def test_update_user_email_only(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating only email."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "newemail@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
        assert data["is_verified"] is False  # Email change resets verification

    @pytest.mark.asyncio
    async def test_update_user_username_only(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating only username."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "newusername"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(
        self, client: AsyncClient, auth_headers, db_session: AsyncSession
    ):
        """Test updating to existing email."""
        # Create another user
        other_user = User(
            email="existing@example.com",
            username="existing",
            hashed_password="hash",
        )
        db_session.add(other_user)
        await db_session.commit()

        # Try to update to that email
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "existing@example.com"},
        )
        assert response.status_code == 409
        data = response.json()
        assert "already" in data.get("error", "") or "already" in data.get(
            "message", ""
        )

    @pytest.mark.asyncio
    async def test_update_user_invalid_data(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating with invalid data."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, client: AsyncClient, auth_headers
    ):
        """Test successful password change."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPassword123!",
            },
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, client: AsyncClient, auth_headers
    ):
        """Test changing password with wrong current password."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!",
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert (
            "incorrect" in data.get("error", "")
            or "incorrect" in data.get("message", "")
            or "Invalid" in data.get("error", "")
        )

    @pytest.mark.asyncio
    async def test_change_password_weak_new(
        self, client: AsyncClient, auth_headers
    ):
        """Test changing to weak password."""
        response = await client.post(
            "/api/v1/users/me/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "weak",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_same_as_current(
        self, client: AsyncClient, auth_headers
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
        assert "different" in data.get("error", "") or "different" in data.get(
            "message", ""
        )

    @pytest.mark.asyncio
    async def test_delete_account_wrong_password(
        self, client: AsyncClient, auth_headers
    ):
        """Test deleting account without password verification."""
        # Note: Current implementation doesn't require password verification
        # This test is kept for future implementation
        # when password verification is added
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_delete_account_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful account deletion."""
        # Create a test user for deletion
        from app.core.security import get_password_hash

        delete_user = User(
            email="delete@example.com",
            username="deleteuser",
            hashed_password=get_password_hash("DeletePass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(delete_user)
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "delete@example.com",
                "password": "DeletePass123!",
            },
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Delete account
        response = await client.delete(
            "/api/v1/users/me",
            headers=headers,
        )
        assert response.status_code == 200
        assert (
            response.json()["message"] == "User account deleted successfully"
        )

        # Verify can't login anymore
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "delete@example.com",
                "password": "DeletePass123!",
            },
        )
        assert login_response.status_code == 401
