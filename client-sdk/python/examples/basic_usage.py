"""Basic usage example for the Full-Stack API Python SDK."""

from fullstack_api import Client
from fullstack_api.exceptions import AuthenticationError, ValidationError


def main():
    """Demonstrate basic SDK usage."""
    # Initialize client
    client = Client(base_url="http://localhost:8000")

    try:
        # Register a new user
        print("Registering new user...")
        user = client.auth.register(
            email="demo@example.com",
            username="demo_user",
            password="DemoPass123!",
            full_name="Demo User",
        )
        print(f"✓ Registered user: {user.username} ({user.email})")

    except ValidationError as e:
        print(f"✗ Registration failed: {e.message}")
        # User might already exist, try logging in

    try:
        # Login
        print("\nLogging in...")
        tokens = client.auth.login(
            username="demo@example.com",  # Can use email or username
            password="DemoPass123!",
        )
        print(f"✓ Logged in successfully")
        print(f"  Access token expires in: {tokens.expires_in} seconds")

        # Get current user
        print("\nFetching user profile...")
        me = client.users.get_current_user()
        print(f"✓ Current user: {me.full_name} ({me.email})")
        print(f"  Account created: {me.created_at}")
        print(f"  Email verified: {me.is_verified}")

        # Update profile
        print("\nUpdating profile...")
        updated = client.users.update_profile(
            full_name="Demo User Updated",
        )
        print(f"✓ Profile updated: {updated.full_name}")

        # Logout
        print("\nLogging out...")
        client.auth.logout()
        print("✓ Logged out successfully")

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
