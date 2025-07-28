"""Main client implementation for the Full-Stack API SDK."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import httpx
from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient
from httpx import Response

from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    UpdateProfileRequest,
    User,
)


class BaseClient:
    """Base client with common functionality."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._token: Optional[Token] = None
        self._token_expires_at: Optional[datetime] = None

    def _handle_response(self, response: Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 204:
            return None

        try:
            data = response.json()
        except json.JSONDecodeError:
            if response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}")
            raise APIError(f"Invalid response: {response.text}")

        if response.status_code >= 200 and response.status_code < 300:
            return data

        # Handle error responses
        error_message = data.get("message", "Unknown error")
        error_code = data.get("code", "unknown_error")
        error_details = data.get("details", {})

        if response.status_code == 401:
            raise AuthenticationError(error_message, details=error_details)
        elif response.status_code == 422:
            raise ValidationError(
                error_message,
                errors=data.get("errors", []),
                details=error_details,
            )
        elif response.status_code == 404:
            raise NotFoundError(error_message, details=error_details)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_message,
                retry_after=int(retry_after) if retry_after else None,
                details=error_details,
            )
        elif response.status_code >= 500:
            raise ServerError(error_message, details=error_details)
        else:
            raise APIError(
                error_message,
                status_code=response.status_code,
                code=error_code,
                details=error_details,
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token.access_token}"
        return headers

    def _should_refresh_token(self) -> bool:
        """Check if token should be refreshed."""
        if not self._token or not self._token_expires_at:
            return False
        # Refresh if token expires in less than 1 minute
        return datetime.utcnow() >= self._token_expires_at - timedelta(minutes=1)


class AuthAPI:
    """Authentication API methods."""

    def __init__(self, client: "Client"):
        """Initialize auth API."""
        self._client = client

    def login(self, username: str, password: str) -> Token:
        """Login with username/email and password."""
        request = LoginRequest(username=username, password=password)
        response = self._client._request(
            "POST",
            "/api/v1/auth/login",
            json=request.model_dump(),
        )
        token = Token(**response)
        self._client._set_token(token)
        return token

    def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """Register a new user."""
        request = RegisterRequest(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
        )
        response = self._client._request(
            "POST",
            "/api/v1/auth/register",
            json=request.model_dump(exclude_none=True),
        )
        return User(**response)

    def refresh_token(self, refresh_token: Optional[str] = None) -> Token:
        """Refresh access token."""
        if not refresh_token and self._client._token:
            refresh_token = self._client._token.refresh_token
        if not refresh_token:
            raise AuthenticationError("No refresh token available")

        request = RefreshTokenRequest(refresh_token=refresh_token)
        response = self._client._request(
            "POST",
            "/api/v1/auth/refresh",
            json=request.model_dump(),
        )
        token = Token(**response)
        self._client._set_token(token)
        return token

    def logout(self) -> None:
        """Logout and invalidate tokens."""
        if self._client._token:
            try:
                self._client._request("POST", "/api/v1/auth/logout")
            except Exception:
                pass  # Ignore logout errors
        self._client._clear_token()


class UsersAPI:
    """Users API methods."""

    def __init__(self, client: "Client"):
        """Initialize users API."""
        self._client = client

    def get_current_user(self) -> User:
        """Get current authenticated user."""
        response = self._client._request("GET", "/api/v1/users/me")
        return User(**response)

    def update_profile(
        self,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        """Update user profile."""
        request = UpdateProfileRequest(email=email, full_name=full_name)
        response = self._client._request(
            "PUT",
            "/api/v1/users/me",
            json=request.model_dump(exclude_none=True),
        )
        return User(**response)

    def delete_account(self, password: str) -> None:
        """Delete user account."""
        self._client._request(
            "DELETE",
            "/api/v1/users/me",
            json={"password": password},
        )
        self._client._clear_token()


class Client(BaseClient):
    """Synchronous client for the Full-Stack API."""

    def __init__(self, *args, **kwargs):
        """Initialize the client."""
        super().__init__(*args, **kwargs)
        self._http_client = HttpxClient(
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        self.auth = AuthAPI(self)
        self.users = UsersAPI(self)

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, *args):
        """Exit context manager."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._http_client.close()

    def _set_token(self, token: Token) -> None:
        """Set authentication token."""
        self._token = token
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=token.expires_in)

    def _clear_token(self) -> None:
        """Clear authentication token."""
        self._token = None
        self._token_expires_at = None

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Any:
        """Make HTTP request."""
        # Auto-refresh token if needed
        if self._should_refresh_token() and path != "/api/v1/auth/refresh":
            self.auth.refresh_token()

        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        response = self._http_client.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )
        return self._handle_response(response)


class AsyncAuthAPI:
    """Async authentication API methods."""

    def __init__(self, client: "AsyncClient"):
        """Initialize auth API."""
        self._client = client

    async def login(self, username: str, password: str) -> Token:
        """Login with username/email and password."""
        request = LoginRequest(username=username, password=password)
        response = await self._client._request(
            "POST",
            "/api/v1/auth/login",
            json=request.model_dump(),
        )
        token = Token(**response)
        self._client._set_token(token)
        return token

    async def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """Register a new user."""
        request = RegisterRequest(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
        )
        response = await self._client._request(
            "POST",
            "/api/v1/auth/register",
            json=request.model_dump(exclude_none=True),
        )
        return User(**response)

    async def refresh_token(self, refresh_token: Optional[str] = None) -> Token:
        """Refresh access token."""
        if not refresh_token and self._client._token:
            refresh_token = self._client._token.refresh_token
        if not refresh_token:
            raise AuthenticationError("No refresh token available")

        request = RefreshTokenRequest(refresh_token=refresh_token)
        response = await self._client._request(
            "POST",
            "/api/v1/auth/refresh",
            json=request.model_dump(),
        )
        token = Token(**response)
        self._client._set_token(token)
        return token

    async def logout(self) -> None:
        """Logout and invalidate tokens."""
        if self._client._token:
            try:
                await self._client._request("POST", "/api/v1/auth/logout")
            except Exception:
                pass  # Ignore logout errors
        self._client._clear_token()


class AsyncUsersAPI:
    """Async users API methods."""

    def __init__(self, client: "AsyncClient"):
        """Initialize users API."""
        self._client = client

    async def get_current_user(self) -> User:
        """Get current authenticated user."""
        response = await self._client._request("GET", "/api/v1/users/me")
        return User(**response)

    async def update_profile(
        self,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        """Update user profile."""
        request = UpdateProfileRequest(email=email, full_name=full_name)
        response = await self._client._request(
            "PUT",
            "/api/v1/users/me",
            json=request.model_dump(exclude_none=True),
        )
        return User(**response)

    async def delete_account(self, password: str) -> None:
        """Delete user account."""
        await self._client._request(
            "DELETE",
            "/api/v1/users/me",
            json={"password": password},
        )
        self._client._clear_token()


class AsyncClient(BaseClient):
    """Asynchronous client for the Full-Stack API."""

    def __init__(self, *args, **kwargs):
        """Initialize the client."""
        super().__init__(*args, **kwargs)
        self._http_client = HttpxAsyncClient(
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        self.auth = AsyncAuthAPI(self)
        self.users = AsyncUsersAPI(self)

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args):
        """Exit async context manager."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()

    def _set_token(self, token: Token) -> None:
        """Set authentication token."""
        self._token = token
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=token.expires_in)

    def _clear_token(self) -> None:
        """Clear authentication token."""
        self._token = None
        self._token_expires_at = None

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Any:
        """Make HTTP request."""
        # Auto-refresh token if needed
        if self._should_refresh_token() and path != "/api/v1/auth/refresh":
            await self.auth.refresh_token()

        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        response = await self._http_client.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )
        return self._handle_response(response)
