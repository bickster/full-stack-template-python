"""Tests for the Full-Stack API Python SDK client."""

import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fullstack_api import Client
from fullstack_api.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from fullstack_api.models import Token, User
from httpx import Response


@pytest.fixture
def mock_response():
    """Create a mock response."""

    def _mock_response(status_code=200, json_data=None, headers=None):
        response = Mock(spec=Response)
        response.status_code = status_code
        response.headers = headers or {}
        response.json.return_value = json_data or {}
        response.text = json.dumps(json_data) if json_data else ""
        return response

    return _mock_response


@pytest.fixture
def client():
    """Create a test client."""
    return Client(base_url="https://api.example.com")


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_type="Bearer",
        expires_in=900,
    )
    client._set_token(token)
    return client


class TestClient:
    """Test Client class."""

    def test_initialization(self):
        """Test client initialization."""
        client = Client(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
            verify_ssl=False,
        )
        assert client.base_url == "https://api.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.verify_ssl is False

    def test_base_url_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = Client(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_context_manager(self):
        """Test client as context manager."""
        with Client(base_url="https://api.example.com") as client:
            assert client._http_client is not None
        # After exiting, client should be closed
        assert client._http_client._closed is False  # httpx doesn't set _closed

    @patch("httpx.Client.request")
    def test_login_success(self, mock_request, client, mock_response):
        """Test successful login."""
        mock_request.return_value = mock_response(
            status_code=200,
            json_data={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "Bearer",
                "expires_in": 900,
            },
        )

        token = client.auth.login("test@example.com", "password123")

        assert token.access_token == "new_access_token"
        assert token.refresh_token == "new_refresh_token"
        assert client._token == token
        mock_request.assert_called_once()

    @patch("httpx.Client.request")
    def test_login_failure(self, mock_request, client, mock_response):
        """Test failed login."""
        mock_request.return_value = mock_response(
            status_code=401,
            json_data={
                "code": "authentication_error",
                "message": "Invalid credentials",
            },
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.auth.login("test@example.com", "wrong_password")

        assert "Invalid credentials" in str(exc_info.value)

    @patch("httpx.Client.request")
    def test_register_success(self, mock_request, client, mock_response):
        """Test successful registration."""
        user_data = {
            "id": "123",
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        mock_request.return_value = mock_response(
            status_code=201,
            json_data=user_data,
        )

        user = client.auth.register(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"

    @patch("httpx.Client.request")
    def test_validation_error(self, mock_request, client, mock_response):
        """Test validation error handling."""
        mock_request.return_value = mock_response(
            status_code=422,
            json_data={
                "code": "validation_error",
                "message": "Validation failed",
                "errors": [
                    {"field": "email", "message": "Invalid email format"},
                    {"field": "password", "message": "Password too weak"},
                ],
            },
        )

        with pytest.raises(ValidationError) as exc_info:
            client.auth.register(
                email="invalid",
                username="test",
                password="weak",
            )

        assert exc_info.value.errors == [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too weak"},
        ]

    @patch("httpx.Client.request")
    def test_rate_limit_error(self, mock_request, client, mock_response):
        """Test rate limit error handling."""
        mock_request.return_value = mock_response(
            status_code=429,
            json_data={
                "code": "rate_limit_exceeded",
                "message": "Too many requests",
            },
            headers={"Retry-After": "60"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.auth.login("test@example.com", "password")

        assert exc_info.value.retry_after == 60

    @patch("httpx.Client.request")
    def test_get_current_user(self, mock_request, authenticated_client, mock_response):
        """Test getting current user."""
        user_data = {
            "id": "123",
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        mock_request.return_value = mock_response(
            status_code=200,
            json_data=user_data,
        )

        user = authenticated_client.users.get_current_user()

        assert user.email == "test@example.com"
        assert user.username == "testuser"

        # Check authorization header was sent
        call_args = mock_request.call_args
        headers = call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test_access_token"

    @patch("httpx.Client.request")
    def test_auto_token_refresh(
        self, mock_request, authenticated_client, mock_response
    ):
        """Test automatic token refresh."""
        # Set token to expire soon
        authenticated_client._token_expires_at = datetime.utcnow() + timedelta(
            seconds=30
        )

        # Mock refresh token response
        refresh_response = mock_response(
            status_code=200,
            json_data={
                "access_token": "refreshed_access_token",
                "refresh_token": "refreshed_refresh_token",
                "token_type": "Bearer",
                "expires_in": 900,
            },
        )

        # Mock get user response
        user_response = mock_response(
            status_code=200,
            json_data={
                "id": "123",
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        mock_request.side_effect = [refresh_response, user_response]

        # Make request that should trigger refresh
        user = authenticated_client.users.get_current_user()

        assert user.email == "test@example.com"
        assert authenticated_client._token.access_token == "refreshed_access_token"
        assert mock_request.call_count == 2

    @patch("httpx.Client.request")
    def test_logout(self, mock_request, authenticated_client, mock_response):
        """Test logout."""
        mock_request.return_value = mock_response(status_code=204)

        authenticated_client.auth.logout()

        assert authenticated_client._token is None
        assert authenticated_client._token_expires_at is None
        mock_request.assert_called_once()

    @patch("httpx.Client.request")
    def test_not_found_error(self, mock_request, client, mock_response):
        """Test not found error handling."""
        mock_request.return_value = mock_response(
            status_code=404,
            json_data={
                "code": "not_found",
                "message": "User not found",
            },
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.users.get_current_user()

        assert "User not found" in str(exc_info.value)
