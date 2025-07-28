# Comprehensive Testing Guide for Full-Stack Template

This guide provides detailed instructions for setting up and running tests for the Full-Stack Template, including lessons learned from real-world implementation.

## Table of Contents
1. [Overview](#overview)
2. [Environment Setup](#environment-setup)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Best Practices](#best-practices)
7. [Testing Strategy](#testing-strategy)
8. [Continuous Integration](#continuous-integration)

## Overview

The Full-Stack Template uses:
- **Backend**: pytest with async support for FastAPI
- **Frontend**: Vitest for React/TypeScript
- **Coverage**: 80% minimum for production readiness

### Key Principles

> **Note**: For testing philosophy and quality-first development approach, see [CLAUDE.md](../../CLAUDE.md#testing-philosophy).

Additional testing principles:
- **Test Smart**: Focus on critical paths and business logic
- **Test Realistically**: Use proper async patterns and real dependencies

## Environment Setup

### Prerequisites

1. **Python Dependencies**
```bash
# requirements.txt - MUST include these for async testing
sqlalchemy>=2.0.23
asyncpg>=0.29.0        # Critical for async PostgreSQL
psycopg2-binary>=2.9.9 # Keep for migrations
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.25.0         # For async HTTP testing
```

2. **Test Environment Configuration**
```bash
# Create test environment file immediately
cp .env.example .env.test

# Edit .env.test
TESTING=1
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/test_db
SECRET_KEY=test-secret-key-only-for-testing
```

3. **Database Setup**
```bash
# Ensure PostgreSQL is running
docker run -d \
  --name postgres-test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  postgres:15
```

### Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

## Backend Testing

### Project Structure
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # No database required
│   ├── test_security.py
│   ├── test_utils.py
│   └── test_validators.py
├── integration/         # Database required
│   ├── test_auth_endpoints.py
│   ├── test_user_endpoints.py
│   └── test_database.py
└── functional/          # End-to-end tests
    └── test_user_flows.py
```

### Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -ra
    --strict-markers
    --cov=src
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=70  # Start with 70%, increase gradually

[coverage:run]
source = src
omit =
    */tests/*
    */migrations/*
    */__init__.py
    */config_production.py  # Exclude production-only files
    */cli/*                 # Exclude CLI if not critical

[coverage:report]
precision = 2
show_missing = True
skip_covered = True
```

### Essential Fixtures (conftest.py)
```python
import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.api.main import app
from app.db.models import Base, User
from app.core.config import settings
from app.core.security import get_password_hash

# Override settings for testing
settings.TESTING = True
settings.DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    async def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

### Writing Tests

#### Unit Tests (No Database)
```python
# tests/unit/test_security.py
import pytest
from datetime import datetime, timezone, timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token
)

class TestPasswordHashing:
    def test_password_hash_is_different_from_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert password != hashed
        assert password not in hashed

    def test_verify_password_correct(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

class TestJWTTokens:
    def test_create_access_token(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded["sub"] == "user123"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_token_expiration(self):
        data = {"sub": "user123"}
        # Create token that expires in 1 second
        token = create_access_token(data, timedelta(seconds=1))

        # Should be valid immediately
        decoded = decode_token(token)
        assert decoded["sub"] == "user123"

        # Wait for expiration
        import time
        time.sleep(2)

        # Should raise exception
        with pytest.raises(Exception):  # Replace with your specific exception
            decode_token(token)
```

#### Integration Tests (With Database)
```python
# tests/integration/test_auth_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123!",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data  # Security check

@pytest.mark.asyncio
async def test_login_valid_credentials(client: AsyncClient, test_user):
    """Test login with valid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_CREDENTIALS"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, auth_headers):
    """Test getting current user information."""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests (fast, no DB)
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_security.py -v

# Run with specific markers
pytest -m "not slow" -v

# Run with output
pytest -s -v

# Run until first failure
pytest -x

# Run failed tests from last run
pytest --lf
```

## Frontend Testing

### Setup (vitest.config.ts)
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData/*',
      ],
      thresholds: {
        branches: 70,
        functions: 70,
        lines: 70,
        statements: 70
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
```

### Test Setup File
```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Clear all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock React Router
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Navigate: vi.fn(() => null),
    useNavigate: vi.fn(() => vi.fn()),
  };
});
```

### Example Frontend Tests
```typescript
// src/stores/authStore.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from './authStore';

describe('Auth Store', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      tokens: null,
      isAuthenticated: false
    });
  });

  it('should login successfully', async () => {
    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login({
        username: 'testuser',
        password: 'password123'
      });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).not.toBeNull();
  });

  it('should logout successfully', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});
```

## Common Issues & Solutions

> **Note**: For common testing issues and quick solutions, see [CLAUDE.md](../../CLAUDE.md#testing-issues).

### Additional Testing Issues

#### Database Connection Issues
```
Connection refused: Is the server running on host "localhost"
```

**Solution**:
```bash
# Start PostgreSQL with Docker
docker run -d \
  --name postgres-test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  postgres:15

# Verify connection
docker exec -it postgres-test psql -U postgres -d test_db
```

#### Datetime Deprecation Warnings
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated
```

**Solution**:
```python
# Old (deprecated)
from datetime import datetime
expire = datetime.utcnow() + timedelta(minutes=15)

# New (correct)
from datetime import datetime, timezone
expire = datetime.now(timezone.utc) + timedelta(minutes=15)
```

## Frontend Testing Common Issues

### 1. Third-Party UI Component Testing
```
Unable to find an element with the role "img"
```

**Problem**: Ant Design components don't always use expected ARIA roles

**Solution**:
```typescript
// ❌ Wrong - assuming ARIA role
const spinner = screen.getByRole('img');

// ✅ Correct - query by actual attributes
const spinner = document.querySelector('[aria-busy="true"]');
expect(spinner).toHaveClass('ant-spin-spinning');
```

### 2. React Router Mock Issues
```
Expected: { to: '/login' }, {}
Received: { to: '/login' }, undefined
```

**Problem**: React passes undefined, not empty object as second argument

**Solution**:
```typescript
// ❌ Wrong expectation
expect(Navigate).toHaveBeenCalledWith({ to: '/login' }, {});

// ✅ Correct expectation
expect(Navigate).toHaveBeenCalledWith(
  { to: '/login', replace: true },
  undefined
);
```

### 3. Mock State Persistence
**Problem**: Tests interfere with each other due to persistent mock state

**Solution**:
```typescript
beforeEach(() => {
  vi.clearAllMocks();  // Clear all mock state
  // Reset store state
  useAuthStore.setState({
    user: null,
    token: null
  });
});
```

### 4. Zustand Act Warnings
```
Warning: An update to useAuthStore inside a test was not wrapped in act(...)
```

**Solution**: These warnings are expected and normal - document them:
```typescript
// This will show act() warnings - that's normal
const { result } = renderHook(() => useAuthStore());
// The warnings don't affect test results
```

### 5. Coverage Dependencies Missing
```
Error: Missing @vitest/coverage-v8
```

**Solution**: Install coverage dependencies upfront:
```bash
npm install --save-dev @vitest/coverage-v8
```

### 6. Component Props Testing
**Problem**: Partial prop expectations fail

**Solution**: Include all props in expectations:
```typescript
// ❌ Partial expectation
expect(Navigate).toHaveBeenCalledWith(
  expect.objectContaining({ to: '/login' })
);

// ✅ Complete expectation
expect(Navigate).toHaveBeenCalledWith(
  { to: '/login', replace: true, state: { from: location } },
  undefined
);
```

## Best Practices

### 1. Test Organization
- **Unit tests**: Pure functions, no external dependencies
- **Integration tests**: Database and API interactions
- **Functional tests**: Complete user workflows

### 2. Fixture Management
- Use session-scoped fixtures for expensive operations
- Clean up after each test with transactions
- Mock external services consistently

### 3. Async Testing
```python
# Always use pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

# Or configure asyncio_mode = auto in pytest.ini
```

### 4. Test Data
```python
# Use factories for test data
from faker import Faker
fake = Faker()

def create_test_user():
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "TestPass123!",
        "full_name": fake.name()
    }
```

### 5. Error Testing
```python
# Test both success and failure paths
async def test_endpoint_success(client):
    response = await client.post("/endpoint", json=valid_data)
    assert response.status_code == 200

async def test_endpoint_validation_error(client):
    response = await client.post("/endpoint", json=invalid_data)
    assert response.status_code == 422
    assert "validation_error" in response.json()["code"]
```

## Testing Strategy

### Coverage Goals

#### Backend Coverage
1. **Critical Security Functions**: 95%+
2. **Business Logic**: 90%+
3. **API Endpoints**: 85%+
4. **Utilities**: 80%+
5. **Overall**: 80%+

#### Frontend Coverage (Realistic Progression)
1. **Initial Goal**: 50% (focus on critical paths)
2. **3 Months**: 60% (add edge cases)
3. **6 Months**: 70% (comprehensive testing)
4. **Mature**: 80%+ (full coverage)

#### Coverage Configuration
```ini
# pytest.ini (backend)
[coverage:run]
omit =
    */tests/*
    */migrations/*
    */alembic/*
    */__pycache__/*
    */config_production.py

[coverage:report]
fail_under = 70  # Start realistic, increase over time
```

```typescript
// vitest.config.ts (frontend)
coverage: {
  thresholds: {
    branches: 50,    // Start low
    functions: 50,   // Increase gradually
    lines: 50,       // As codebase matures
    statements: 50
  },
  exclude: [
    'node_modules',
    'dist',
    '**/*.d.ts',
    '**/*.config.*',
    '**/mockServiceWorker.js',
    'src/main.tsx',
    'src/vite-env.d.ts'
  ]
}

### Test Pyramid
```
         /\
        /  \    E2E Tests (10%)
       /    \   - Full user flows
      /------\
     /        \ Integration Tests (30%)
    /          \- API endpoints
   /            - Database operations
  /--------------\
 /                \ Unit Tests (60%)
/                  - Business logic
                   - Utilities
                   - Validators
```

### Performance Testing
```python
# Add performance markers
@pytest.mark.slow
async def test_bulk_operation():
    # Test that takes > 1 second
    pass

# Run excluding slow tests
pytest -m "not slow"
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt -r requirements-dev.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:password@localhost/test_db
        TESTING: "1"
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Debugging Tests

### Useful Commands
```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Run specific test by name pattern
pytest -k "test_login"

# Show slowest tests
pytest --durations=10

# Parallel execution
pytest -n auto
```

### VSCode Configuration
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests",
    "-v",
    "--no-cov"  // Disable coverage in IDE for speed
  ]
}
```

## Conclusion

Successful testing requires:
1. **Proper setup** with async dependencies
2. **Test organization** that matches your needs
3. **Immediate testing** after implementation
4. **Realistic goals** that grow over time
5. **Good fixtures** that simplify test writing

Remember: Tests are not a burden, they're your safety net for confident deployments and refactoring.
