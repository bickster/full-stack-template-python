"""Error handling example for the Full-Stack API Python SDK."""

from fullstack_api import Client
from fullstack_api.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def demonstrate_validation_errors():
    """Show how to handle validation errors."""
    client = Client(base_url="http://localhost:8000")

    print("Testing validation errors...")

    # Invalid email
    try:
        client.auth.register(
            email="not-an-email",
            username="test",
            password="pass",
            full_name="Test User",
        )
    except ValidationError as e:
        print(f"✓ Caught validation error: {e.message}")
        if e.errors:
            print("  Validation errors:")
            for error in e.errors:
                print(f"    - {error}")

    # Weak password
    try:
        client.auth.register(
            email="test@example.com",
            username="test",
            password="weak",
            full_name="Test User",
        )
    except ValidationError as e:
        print(f"✓ Caught weak password: {e.message}")

    # Missing required fields
    try:
        client.auth.login(username="", password="")
    except ValidationError as e:
        print(f"✓ Caught missing fields: {e.message}")


def demonstrate_auth_errors():
    """Show how to handle authentication errors."""
    client = Client(base_url="http://localhost:8000")

    print("\nTesting authentication errors...")

    # Invalid credentials
    try:
        client.auth.login(
            username="nonexistent@example.com",
            password="wrongpassword",
        )
    except AuthenticationError as e:
        print(f"✓ Caught auth error: {e.message}")

    # Accessing protected endpoint without auth
    try:
        client.users.get_current_user()
    except AuthenticationError as e:
        print(f"✓ Caught unauthorized access: {e.message}")

    # Expired token simulation
    client._token = None  # Clear token
    try:
        client.users.get_current_user()
    except AuthenticationError as e:
        print(f"✓ Caught missing token: {e.message}")


def demonstrate_rate_limiting():
    """Show how to handle rate limiting."""
    client = Client(base_url="http://localhost:8000")

    print("\nTesting rate limiting...")

    # Make rapid requests
    attempt = 0
    while attempt < 10:
        try:
            attempt += 1
            # Rapid login attempts
            client.auth.login(
                username="test@example.com",
                password="wrong",
            )
        except RateLimitError as e:
            print(f"✓ Rate limited after {attempt} attempts")
            print(f"  Message: {e.message}")
            if e.retry_after:
                print(f"  Retry after: {e.retry_after} seconds")
            break
        except AuthenticationError:
            # Expected for wrong password
            pass


def demonstrate_error_recovery():
    """Show error recovery patterns."""
    client = Client(base_url="http://localhost:8000")

    print("\nDemonstrating error recovery...")

    # Pattern 1: Retry with exponential backoff
    import time

    def retry_with_backoff(func, max_retries=3):
        """Retry function with exponential backoff."""
        for i in range(max_retries):
            try:
                return func()
            except (APIError, RateLimitError) as e:
                if i == max_retries - 1:
                    raise
                wait_time = 2**i  # Exponential backoff
                print(f"  Retry {i + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)

    # Pattern 2: Fallback behavior
    def get_user_safe(client):
        """Get user with fallback."""
        try:
            return client.users.get_current_user()
        except AuthenticationError:
            print("  Not authenticated, using guest mode")
            return None
        except APIError as e:
            print(f"  API error, using cached data: {e}")
            return {"username": "cached_user", "email": "cached@example.com"}

    # Pattern 3: Circuit breaker
    class CircuitBreaker:
        """Simple circuit breaker implementation."""

        def __init__(self, failure_threshold=3, recovery_timeout=60):
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self.failures = 0
            self.last_failure_time = None
            self.is_open = False

        def call(self, func):
            """Call function with circuit breaker."""
            if self.is_open:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.is_open = False
                    self.failures = 0
                else:
                    raise APIError("Circuit breaker is open")

            try:
                result = func()
                self.failures = 0
                return result
            except APIError:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    self.is_open = True
                    print(f"  Circuit breaker opened after {self.failures} failures")
                raise

    print("✓ Error recovery patterns demonstrated")


def main():
    """Run all error handling demonstrations."""
    print("Error Handling Examples")
    print("=" * 50)

    try:
        demonstrate_validation_errors()
        demonstrate_auth_errors()
        demonstrate_rate_limiting()
        demonstrate_error_recovery()
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {e}")

    print("\n✓ Error handling examples completed")


if __name__ == "__main__":
    main()
