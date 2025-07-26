"""Database initialization."""

import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.user import User
from app.db.session import AsyncSessionLocal, engine


async def create_superuser(db: AsyncSession) -> Optional[User]:
    """Create the first superuser."""
    # Check if superuser already exists
    result = await db.execute(
        select(User).where(User.is_superuser == True)
    )
    existing_superuser = result.scalar_one_or_none()
    
    if existing_superuser:
        print("Superuser already exists")
        return existing_superuser
    
    # Create superuser
    superuser = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    
    db.add(superuser)
    await db.commit()
    await db.refresh(superuser)
    
    print(f"Superuser created: {superuser.email}")
    return superuser


async def init_db() -> None:
    """Initialize database with default data."""
    async with AsyncSessionLocal() as db:
        # Create superuser
        await create_superuser(db)
        
        # Add any other initialization logic here
        print("Database initialization complete")


async def check_db_connection() -> bool:
    """Check if database is accessible."""
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(init_db())