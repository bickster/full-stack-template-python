#!/usr/bin/env python3
"""Database setup script."""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.init_db import check_db_connection, init_db  # noqa: E402


async def wait_for_db(max_retries: int = 30, retry_interval: int = 2) -> bool:
    """Wait for database to be ready."""
    print("Waiting for database to be ready...")

    for i in range(max_retries):
        if await check_db_connection():
            print("Database is ready!")
            return True

        print(
            f"Database not ready, retrying in {retry_interval}s... "
            f"({i+1}/{max_retries})"
        )
        time.sleep(retry_interval)

    print("Database connection failed after maximum retries")
    return False


async def main():
    """Run the main setup function."""
    # Wait for database
    if not await wait_for_db():
        sys.exit(1)

    # Initialize database
    print("Initializing database...")
    await init_db()

    print("Database setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
