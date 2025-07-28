# Full-Stack API Python SDK

A Python SDK for interacting with the Full-Stack API, providing type-safe methods for authentication and user management.

## Installation

```bash
pip install fullstack-api-client
```

## Quick Start

```python
from fullstack_api import Client

# Initialize the client
client = Client(base_url="https://api.example.com")

# Login
tokens = client.auth.login(username="user@example.com", password="password123")

# The client automatically handles token storage
# Access protected resources
user = client.users.get_current_user()
print(f"Logged in as: {user.email}")

# Logout
client.auth.logout()
```

## Features

- 🔐 **Automatic token management** - Handles access/refresh token rotation
- 🦺 **Type safety** - Full type hints and Pydantic models
- 🚀 **Async support** - Both sync and async methods available
- 🛡️ **Error handling** - Structured error responses
- 📦 **Zero configuration** - Works out of the box

## Usage

### Authentication

```python
from fullstack_api import Client
from fullstack_api.exceptions import AuthenticationError

client = Client(base_url="https://api.example.com")

try:
    # Register a new user
    user = client.auth.register(
        email="newuser@example.com",
        username="newuser",
        password="SecurePass123!",
        full_name="New User"
    )

    # Login
    tokens = client.auth.login(
        username="newuser@example.com",
        password="SecurePass123!"
    )

    # Refresh token (handled automatically, but can be done manually)
    new_tokens = client.auth.refresh_token()

except AuthenticationError as e:
    print(f"Authentication failed: {e.detail}")
```

### User Management

```python
# Get current user
me = client.users.get_current_user()

# Update user profile
updated = client.users.update_profile(
    full_name="Updated Name",
    email="newemail@example.com"
)

# Delete account
client.users.delete_account(password="SecurePass123!")
```

### Async Support

```python
import asyncio
from fullstack_api import AsyncClient

async def main():
    async with AsyncClient(base_url="https://api.example.com") as client:
        # All methods available in async version
        tokens = await client.auth.login(
            username="user@example.com",
            password="password123"
        )

        user = await client.users.get_current_user()
        print(f"Logged in as: {user.email}")

asyncio.run(main())
```

### Error Handling

```python
from fullstack_api.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError
)

try:
    user = client.users.get_current_user()
except AuthenticationError:
    # Token expired or invalid
    client.auth.refresh_token()
except ValidationError as e:
    # Invalid request data
    print(f"Validation errors: {e.errors}")
except RateLimitError as e:
    # Too many requests
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except APIError as e:
    # General API error
    print(f"API error: {e.status_code} - {e.detail}")
```

### Configuration

```python
from fullstack_api import Client

client = Client(
    base_url="https://api.example.com",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Number of retries for failed requests
    verify_ssl=True,  # SSL certificate verification
)
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/fullstack-api-python.git
cd fullstack-api-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fullstack_api

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
