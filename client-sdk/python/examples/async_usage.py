"""Async usage example for the Full-Stack API Python SDK."""

import asyncio

from fullstack_api import AsyncClient
from fullstack_api.exceptions import AuthenticationError, RateLimitError


async def demonstrate_rate_limiting(client: AsyncClient):
    """Demonstrate handling rate limiting."""
    print("\nTesting rate limiting...")

    # Make multiple rapid login attempts
    for i in range(10):
        try:
            await client.auth.login(
                username="test@example.com",
                password="wrong_password",
            )
        except AuthenticationError:
            print(f"  Attempt {i + 1}: Invalid credentials")
        except RateLimitError as e:
            print(f"  Attempt {i + 1}: Rate limited!")
            if e.retry_after:
                print(f"  Retry after: {e.retry_after} seconds")
            break
        except Exception as e:
            print(f"  Attempt {i + 1}: {e}")


async def demonstrate_auto_refresh(client: AsyncClient):
    """Demonstrate automatic token refresh."""
    print("\nDemonstrating auto token refresh...")

    # Login first
    await client.auth.login(
        username="demo@example.com",
        password="DemoPass123!",
    )
    print("✓ Logged in")

    # Simulate waiting for token to near expiration
    print("  Simulating API calls over time...")

    # Make multiple API calls - the SDK will auto-refresh when needed
    for i in range(5):
        user = await client.users.get_current_user()
        print(f"  Call {i + 1}: User {user.username} still authenticated")
        await asyncio.sleep(1)


async def main():
    """Demonstrate async SDK usage."""
    # Use async context manager for automatic cleanup
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Basic authentication flow
        try:
            print("Async SDK Example")
            print("=" * 50)

            # Register
            print("\nRegistering user...")
            try:
                user = await client.auth.register(
                    email="async_demo@example.com",
                    username="async_demo",
                    password="AsyncPass123!",
                    full_name="Async Demo User",
                )
                print(f"✓ Registered: {user.username}")
            except Exception:
                print("  User already exists")

            # Login
            print("\nLogging in...")
            tokens = await client.auth.login(
                username="async_demo@example.com",
                password="AsyncPass123!",
            )
            print("✓ Logged in successfully")

            # Concurrent API calls
            print("\nMaking concurrent API calls...")
            tasks = [
                client.users.get_current_user(),
                client.users.get_current_user(),
                client.users.get_current_user(),
            ]

            # All three calls execute concurrently
            results = await asyncio.gather(*tasks)
            print(f"✓ Made {len(results)} concurrent calls")

            # Demonstrate error handling
            await demonstrate_rate_limiting(client)

            # Demonstrate auto token refresh
            await demonstrate_auto_refresh(client)

        except Exception as e:
            print(f"\n✗ Error: {e}")

        print("\n✓ Client closed automatically via context manager")


if __name__ == "__main__":
    asyncio.run(main())
