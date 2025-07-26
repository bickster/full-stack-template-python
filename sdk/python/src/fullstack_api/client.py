"""FullStack API Client."""

import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .exceptions import (
    FullStackAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    ServerError,
)
from .storage import TokenStorage, MemoryTokenStorage
from .types import (
    AuthTokens,
    User,
    LoginRequest,
    RegisterRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    HealthCheck,
)


class FullStackClient:
    """FullStack API Client."""

    def __init__(
        self,
        base_url: str,
        token_storage: Optional[TokenStorage] = None,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """Initialize client.
        
        Args:
            base_url: API base URL
            token_storage: Token storage implementation
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.token_storage = token_storage or MemoryTokenStorage()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _get_url(self, path: str) -> str:
        """Get full URL for path."""
        return urljoin(self.base_url, path)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        token = self.token_storage.get_access_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response."""
        try:
            response.raise_for_status()
        except requests.HTTPError:
            self._handle_error(response)
        
        # Return None for 204 No Content
        if response.status_code == 204:
            return None
        
        try:
            return response.json()
        except ValueError:
            return response.text

    def _handle_error(self, response: requests.Response) -> None:
        """Handle error response."""
        try:
            error_data = response.json()
            message = error_data.get("error", "Unknown error")
            code = error_data.get("code")
            details = error_data.get("details", {})
        except ValueError:
            message = response.text or "Unknown error"
            code = None
            details = {}
        
        status_code = response.status_code
        
        if status_code == 401:
            raise AuthenticationError(message, code, details, status_code)
        elif status_code == 422:
            raise ValidationError(message, code, details, status_code)
        elif status_code == 429:
            raise RateLimitError(message, code, details, status_code)
        elif status_code == 404:
            raise NotFoundError(message, code, details, status_code)
        elif status_code >= 500:
            raise ServerError(message, code, details, status_code)
        else:
            raise FullStackAPIError(message, code, details, status_code)

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: bool = True,
        retry_on_401: bool = True,
    ) -> Any:
        """Make API request."""
        url = self._get_url(path)
        headers = {}
        
        if auth:
            headers.update(self._get_auth_headers())
        
        response = self.session.request(
            method,
            url,
            json=data,
            params=params,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        
        # Handle token refresh on 401
        if response.status_code == 401 and auth and retry_on_401:
            refresh_token = self.token_storage.get_refresh_token()
            if refresh_token:
                try:
                    tokens = self.refresh_access_token(refresh_token)
                    self.token_storage.set_tokens(tokens)
                    
                    # Retry request with new token
                    headers.update(self._get_auth_headers())
                    response = self.session.request(
                        method,
                        url,
                        json=data,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                        verify=self.verify_ssl,
                    )
                except (AuthenticationError, FullStackAPIError):
                    # Refresh failed, clear tokens
                    self.token_storage.clear_tokens()
        
        return self._handle_response(response)

    # Health check
    def health_check(self) -> HealthCheck:
        """Check API health status."""
        data = self._request("GET", "/health", auth=False)
        return HealthCheck.from_dict(data)

    # Authentication
    def login(self, request: LoginRequest) -> AuthTokens:
        """Login user."""
        data = self._request(
            "POST",
            "/api/v1/auth/login",
            data={"username": request.username, "password": request.password},
            auth=False,
        )
        tokens = AuthTokens(**data)
        self.token_storage.set_tokens(tokens)
        return tokens

    def register(self, request: RegisterRequest) -> User:
        """Register new user."""
        data = self._request(
            "POST",
            "/api/v1/auth/register",
            data={
                "email": request.email,
                "username": request.username,
                "password": request.password,
                "full_name": request.full_name,
            },
            auth=False,
        )
        return User.from_dict(data)

    def logout(self) -> None:
        """Logout current user."""
        try:
            self._request("POST", "/api/v1/auth/logout")
        finally:
            self.token_storage.clear_tokens()

    def refresh_access_token(self, refresh_token: str) -> AuthTokens:
        """Refresh access token."""
        data = self._request(
            "POST",
            "/api/v1/auth/refresh",
            data={"refresh_token": refresh_token},
            auth=False,
            retry_on_401=False,
        )
        return AuthTokens(**data)

    def request_password_reset(self, request: PasswordResetRequest) -> Dict[str, str]:
        """Request password reset."""
        return self._request(
            "POST",
            "/api/v1/auth/password-reset",
            data={"email": request.email},
            auth=False,
        )

    def confirm_password_reset(self, request: PasswordResetConfirm) -> Dict[str, str]:
        """Confirm password reset."""
        return self._request(
            "POST",
            "/api/v1/auth/password-reset/confirm",
            data={"token": request.token, "new_password": request.new_password},
            auth=False,
        )

    # User management
    def get_current_user(self) -> User:
        """Get current user."""
        data = self._request("GET", "/api/v1/users/me")
        return User.from_dict(data)

    def update_current_user(self, request: UpdateUserRequest) -> User:
        """Update current user."""
        data = self._request("PATCH", "/api/v1/users/me", data=request.to_dict())
        return User.from_dict(data)

    def change_password(self, request: ChangePasswordRequest) -> Dict[str, str]:
        """Change password."""
        return self._request(
            "POST",
            "/api/v1/users/me/change-password",
            data={
                "old_password": request.old_password,
                "new_password": request.new_password,
            },
        )

    def delete_account(self, password: str) -> Dict[str, str]:
        """Delete current user account."""
        result = self._request(
            "DELETE",
            "/api/v1/users/me",
            data={"password": password},
        )
        self.token_storage.clear_tokens()
        return result

    # Utility methods
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.token_storage.get_access_token() is not None

    def set_tokens(self, tokens: AuthTokens) -> None:
        """Set tokens manually."""
        self.token_storage.set_tokens(tokens)

    def clear_tokens(self) -> None:
        """Clear stored tokens."""
        self.token_storage.clear_tokens()

    def get_tokens(self) -> Dict[str, Optional[str]]:
        """Get current tokens."""
        return {
            "access_token": self.token_storage.get_access_token(),
            "refresh_token": self.token_storage.get_refresh_token(),
        }