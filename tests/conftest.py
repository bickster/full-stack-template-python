"""Global test configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.core.security import get_password_hash
from app.db.models.base import Base
from app.db.models.user import User
from app.db.session import get_db

fake = Faker()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create an async session for testing."""
    # Create an in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()

    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_data() -> Dict[str, str]:
    """Generate random user data."""
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "TestPass123!",
    }


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create a test superuser."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPass123!"),
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Create authentication headers."""
    from app.core.security import create_access_token

    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superuser_auth_headers(test_superuser: User) -> Dict[str, str]:
    """Create superuser authentication headers."""
    from app.core.security import create_access_token

    token = create_access_token(subject=str(test_superuser.id))
    return {"Authorization": f"Bearer {token}"}
