# FullStack API Python Client

Official Python client library for the FullStack API.

## Installation

```bash
pip install fullstack-api-client
```

For async support:
```bash
pip install fullstack-api-client[async]
```

## Quick Start

```python
from fullstack_api import FullStackClient, LoginRequest

# Create client instance
client = FullStackClient("https://api.example.com")

# Login
tokens = client.login(LoginRequest(
    username="john_doe",
    password="SecurePassword123!"
))

# Get current user
user = client.get_current_user()
print(f"Hello, {user.username}!")
```

## Features

- 🔐 Automatic token management with refresh
- 🔄 Built-in retry logic with exponential backoff
- 📝 Full type hints and dataclasses
- 💾 Multiple token storage options
- 🛡️ Comprehensive error handling
- 🚀 Simple and intuitive API
- ⚡ Optional async support

## Usage

### Creating a Client

```python
from fullstack_api import FullStackClient

# Basic usage
client = FullStackClient("https://api.example.com")

# With custom configuration
client = FullStackClient(
    base_url="https://api.example.com",
    timeout=60,  # Request timeout in seconds
    max_retries=5,  # Maximum retry attempts
    verify_ssl=True  # SSL certificate verification
)
```

### Token Storage

The client supports different token storage strategies:

#### In-Memory Storage (Default)
```python
from fullstack_api import FullStackClient, MemoryTokenStorage

client = FullStackClient(
    "https://api.example.com",
    token_storage=MemoryTokenStorage()
)
```

#### File-Based Storage
```python
from fullstack_api import FullStackClient, FileTokenStorage

# Default location: ~/.fullstack/tokens.json
client = FullStackClient(
    "https://api.example.com",
    token_storage=FileTokenStorage()
)

# Custom location
client = FullStackClient(
    "https://api.example.com",
    token_storage=FileTokenStorage("/path/to/tokens.json")
)
```

#### Custom Storage
```python
from fullstack_api import TokenStorage, AuthTokens

class CustomTokenStorage(TokenStorage):
    def get_access_token(self) -> Optional[str]:
        # Your implementation
        pass
    
    def get_refresh_token(self) -> Optional[str]:
        # Your implementation
        pass
    
    def set_tokens(self, tokens: AuthTokens) -> None:
        # Your implementation
        pass
    
    def clear_tokens(self) -> None:
        # Your implementation
        pass

client = FullStackClient(
    "https://api.example.com",
    token_storage=CustomTokenStorage()
)
```

### Authentication

#### Register
```python
from fullstack_api import RegisterRequest

user = client.register(RegisterRequest(
    email="john@example.com",
    username="john_doe",
    password="SecurePassword123!",
    full_name="John Doe"  # Optional
))
```

#### Login
```python
from fullstack_api import LoginRequest

tokens = client.login(LoginRequest(
    username="john_doe",
    password="SecurePassword123!"
))
# Tokens are automatically stored
```

#### Logout
```python
client.logout()
# Tokens are automatically cleared
```

#### Check Authentication Status
```python
if client.is_authenticated():
    print("User is logged in")
```

### User Management

#### Get Current User
```python
user = client.get_current_user()
print(f"ID: {user.id}")
print(f"Email: {user.email}")
print(f"Username: {user.username}")
print(f"Created: {user.created_at}")
```

#### Update User Profile
```python
from fullstack_api import UpdateUserRequest

updated_user = client.update_current_user(UpdateUserRequest(
    email="newemail@example.com",
    full_name="John Smith"
))
```

#### Change Password
```python
from fullstack_api import ChangePasswordRequest

client.change_password(ChangePasswordRequest(
    old_password="OldPassword123!",
    new_password="NewPassword456!"
))
```

#### Delete Account
```python
client.delete_account(password="currentPassword")
```

### Password Reset

#### Request Password Reset
```python
from fullstack_api import PasswordResetRequest

client.request_password_reset(PasswordResetRequest(
    email="john@example.com"
))
```

#### Confirm Password Reset
```python
from fullstack_api import PasswordResetConfirm

client.confirm_password_reset(PasswordResetConfirm(
    token="reset-token-from-email",
    new_password="NewPassword789!"
))
```

### Health Check

```python
health = client.health_check()
print(f"Status: {health.status}")
print(f"Database: {health.database}")
print(f"Version: {health.version}")
```

### Error Handling

```python
from fullstack_api import (
    FullStackAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    ServerError,
)

try:
    client.login(LoginRequest(username="john", password="wrong"))
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Error code: {e.code}")
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors:
        print(f"  - {error['field']}: {error['message']}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except NotFoundError as e:
    print("Resource not found")
except ServerError as e:
    print("Server error occurred")
except FullStackAPIError as e:
    print(f"API error: {e.message}")
```

### Manual Token Management

```python
# Get current tokens
tokens = client.get_tokens()
print(f"Access token: {tokens['access_token']}")
print(f"Refresh token: {tokens['refresh_token']}")

# Set tokens manually
from fullstack_api import AuthTokens

client.set_tokens(AuthTokens(
    access_token="new-access-token",
    refresh_token="new-refresh-token",
    token_type="bearer"
))

# Clear tokens
client.clear_tokens()
```

## Advanced Usage

### Custom Session Configuration

```python
import requests
from fullstack_api import FullStackClient

# Create custom session
session = requests.Session()
session.proxies = {"http": "http://proxy.example.com:8080"}
session.verify = "/path/to/ca-bundle.crt"

# Create client with custom session
client = FullStackClient("https://api.example.com")
client.session = session
```

### Timeout Handling

```python
from requests.exceptions import Timeout

try:
    user = client.get_current_user()
except Timeout:
    print("Request timed out")
```

### SSL Certificate Verification

```python
# Disable SSL verification (not recommended for production)
client = FullStackClient(
    "https://api.example.com",
    verify_ssl=False
)

# Use custom CA bundle
client = FullStackClient("https://api.example.com")
client.session.verify = "/path/to/ca-bundle.crt"
```

## Examples

### CLI Application

```python
#!/usr/bin/env python3
"""FullStack CLI client example."""

import os
import sys
from getpass import getpass

from fullstack_api import (
    FullStackClient,
    FileTokenStorage,
    LoginRequest,
    AuthenticationError,
)

def main():
    # Create client with file-based token storage
    client = FullStackClient(
        os.getenv("FULLSTACK_API_URL", "https://api.example.com"),
        token_storage=FileTokenStorage()
    )
    
    # Check if already authenticated
    if client.is_authenticated():
        try:
            user = client.get_current_user()
            print(f"Logged in as: {user.username}")
            return
        except AuthenticationError:
            # Token expired, need to login again
            client.clear_tokens()
    
    # Login
    username = input("Username: ")
    password = getpass("Password: ")
    
    try:
        client.login(LoginRequest(username=username, password=password))
        user = client.get_current_user()
        print(f"Successfully logged in as: {user.username}")
    except AuthenticationError as e:
        print(f"Login failed: {e.message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Django Integration

```python
# settings.py
FULLSTACK_API_URL = "https://api.example.com"

# views.py
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from fullstack_api import FullStackClient, LoginRequest, AuthenticationError

def fullstack_login(request):
    if request.method == "POST":
        client = FullStackClient(settings.FULLSTACK_API_URL)
        
        try:
            tokens = client.login(LoginRequest(
                username=request.POST["username"],
                password=request.POST["password"]
            ))
            
            # Store tokens in session
            request.session["access_token"] = tokens.access_token
            request.session["refresh_token"] = tokens.refresh_token
            
            # Get user data
            user = client.get_current_user()
            
            # Create or update Django user
            # ... your user sync logic here ...
            
            return redirect("dashboard")
            
        except AuthenticationError:
            # Handle login error
            pass
```

### Flask Integration

```python
from flask import Flask, request, session, jsonify
from fullstack_api import FullStackClient, LoginRequest, AuthTokens

app = Flask(__name__)
app.secret_key = "your-secret-key"

def get_client():
    """Get API client with tokens from session."""
    client = FullStackClient("https://api.example.com")
    
    if "access_token" in session:
        client.set_tokens(AuthTokens(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            token_type="bearer"
        ))
    
    return client

@app.route("/api/login", methods=["POST"])
def login():
    client = get_client()
    
    try:
        tokens = client.login(LoginRequest(
            username=request.json["username"],
            password=request.json["password"]
        ))
        
        # Store tokens in session
        session["access_token"] = tokens.access_token
        session["refresh_token"] = tokens.refresh_token
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/user")
def get_user():
    client = get_client()
    
    try:
        user = client.get_current_user()
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401
```

### Async Usage (with aiohttp)

```python
# Install with: pip install fullstack-api-client[async]

import asyncio
from fullstack_api.async_client import AsyncFullStackClient

async def main():
    async with AsyncFullStackClient("https://api.example.com") as client:
        # Login
        await client.login(username="john_doe", password="password")
        
        # Get user
        user = await client.get_current_user()
        print(f"Hello, {user.username}!")
        
        # Logout
        await client.logout()

asyncio.run(main())
```

## Testing

When testing code that uses the FullStack client, you can use the `MemoryTokenStorage` and mock the HTTP requests:

```python
import pytest
from unittest.mock import Mock, patch
from fullstack_api import FullStackClient, MemoryTokenStorage, User

@pytest.fixture
def client():
    return FullStackClient(
        "https://api.example.com",
        token_storage=MemoryTokenStorage()
    )

def test_get_user(client):
    # Mock the response
    mock_user_data = {
        "id": "123",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "is_verified": True,
        "is_superuser": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    with patch.object(client, "_request", return_value=mock_user_data):
        user = client.get_current_user()
        
        assert user.id == "123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
```

## API Reference

### FullStackClient

The main client class for interacting with the FullStack API.

#### Constructor Parameters

- `base_url` (str): The base URL of the API
- `token_storage` (TokenStorage, optional): Token storage implementation
- `timeout` (int, optional): Request timeout in seconds (default: 30)
- `max_retries` (int, optional): Maximum retry attempts (default: 3)
- `verify_ssl` (bool, optional): Whether to verify SSL certificates (default: True)

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `health_check()` | Check API health status | `HealthCheck` |
| `login(request)` | Authenticate user | `AuthTokens` |
| `register(request)` | Register new user | `User` |
| `logout()` | Logout current user | `None` |
| `refresh_access_token(refresh_token)` | Refresh access token | `AuthTokens` |
| `request_password_reset(request)` | Request password reset | `Dict` |
| `confirm_password_reset(request)` | Confirm password reset | `Dict` |
| `get_current_user()` | Get current user info | `User` |
| `update_current_user(request)` | Update user profile | `User` |
| `change_password(request)` | Change password | `Dict` |
| `delete_account(password)` | Delete user account | `Dict` |
| `is_authenticated()` | Check auth status | `bool` |
| `get_tokens()` | Get current tokens | `Dict` |
| `set_tokens(tokens)` | Set tokens manually | `None` |
| `clear_tokens()` | Clear stored tokens | `None` |

### Exceptions

All exceptions inherit from `FullStackAPIError` and include:

- `message`: Human-readable error message
- `code`: Error code from the API
- `details`: Additional error details
- `status_code`: HTTP status code

#### Exception Types

- `AuthenticationError`: Authentication failed (401)
- `ValidationError`: Validation error (422)
- `RateLimitError`: Rate limit exceeded (429)
- `NotFoundError`: Resource not found (404)
- `ServerError`: Server error (5xx)

## Contributing

See the main repository's contributing guidelines.

## License

MIT