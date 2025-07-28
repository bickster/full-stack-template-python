# Core Full-Stack Template Components Analysis

This document extracts the reusable components from the AppStore Metadata Extractor specification that can serve as a template for any full-stack application with authentication.

## Table of Contents
1. [Configuration Management & Common Pitfalls](#configuration-management--common-pitfalls)
2. [Authentication & User Management](#1-authentication--user-management)
3. [API Structure & Patterns](#2-api-structure--patterns)
4. [Frontend Architecture](#3-frontend-architecture)
5. [Database Schema (Auth Only)](#4-database-schema-auth-only)
6. [Security Implementation](#5-security-implementation)
7. [Testing Patterns](#6-testing-patterns)
8. [Deployment Structure](#7-deployment-structure)
9. [WBS Framework Patterns](#8-wbs-framework-patterns)
10. [Development Workflow](#9-development-workflow)
11. [Client SDKs Pattern](#10-client-sdks-pattern)
12. [Common Utilities](#11-common-utilities)
13. [Project Structure Template](#12-project-structure-template)

## Configuration Management

> **Note**: For common configuration pitfalls and troubleshooting, see [CLAUDE.md](../CLAUDE.md#configuration-management-first).

### Multiple Configuration Points
Be aware of ALL configuration locations:
- **Frontend**: .env, .env.local, .env.production, vite.config.ts, src/services/api.ts
- **Backend**: .env, config.py, settings.py, docker-compose.yml
- **Proxy**: vite.config.ts (dev), nginx.conf (production)

---

## 1. Authentication & User Management

### Core Components
- **JWT-based authentication system** with access/refresh tokens
- User registration with email/username validation
- Password complexity requirements with bcrypt hashing (12 rounds)
- Login attempt tracking and rate limiting
- Refresh token management with revocation
- User profile management (GET /me endpoint)
- Account deletion with GDPR compliance

### Key Features
- Access tokens: 15-minute expiry
- Refresh tokens: 30-day expiry
- Maximum 5 active sessions per user
- Rate limiting: 5 login attempts per 15 minutes
- Email verification flow
- Password reset functionality

---

## 2. API Structure & Patterns

### Backend Stack
- **FastAPI** framework with async/await throughout
- RESTful endpoints with consistent patterns
- Pydantic schemas for request/response validation
- Dependency injection for auth and database sessions
- Global error handling with custom exceptions
- API versioning strategy (/api/v1/)
- Security headers middleware
- CORS configuration

### Standard Response Formats
```python
# Success Response
class SuccessResponse(BaseModel):
    message: str
    data: Dict[str, Any]

# Error Response
class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[Dict[str, Any]]
```

### Common HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 429: Too Many Requests
- 500: Internal Server Error

---

## 3. Frontend Architecture

### Tech Stack
- **React 18** + **TypeScript** + **Vite**
- Zustand for state management (auth store pattern)
- React Router v6 with protected routes
- Axios with interceptors for auth token handling
- Form validation with react-hook-form + zod
- Ant Design UI components
- TailwindCSS for styling
- Error boundary and global error handling

### Core Components
```typescript
// Auth Store Structure
interface AuthStore {
  user: User | null;
  tokens: Tokens | null;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

// Protected Route Pattern
<ProtectedRoute>
  <Component />
</ProtectedRoute>
```

### API Client Configuration
- Axios instance with base URL configuration
- Request interceptor for adding auth headers
- Response interceptor for token refresh
- Global error handler for API errors

---

## 4. Database Schema (Auth Only)

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_refresh_tokens_hash (token_hash),
    INDEX idx_refresh_tokens_user (user_id)
);
```

### Login Attempts Table
```sql
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),
    success BOOLEAN NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_login_attempts_email (email),
    INDEX idx_login_attempts_ip (ip_address),
    INDEX idx_login_attempts_time (attempted_at),
    INDEX idx_login_attempts_user_id (user_id)  -- Always index FKs
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_data JSON,
    response_status INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_user_action (user_id, action),
    INDEX idx_audit_created (created_at)
);
```

### Database Migration Best Practices

#### SQLAlchemy Model Definition
```python
# Example model with all best practices
class User(Base):
    __tablename__ = "users"

    # Always use UUID with callable default
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # Use timezone-aware timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Indexes - ALWAYS index foreign keys
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_is_active", "is_active"),
        Index("ix_users_email", "email", unique=True),
    )
```

#### Foreign Key Patterns
```python
# Always specify ondelete behavior explicitly
user_id = Column(
    UUID,
    ForeignKey("users.id", ondelete="CASCADE"),  # For dependent records
    nullable=False,
    index=True  # Or use __table_args__
)

# For optional relationships
user_id = Column(
    UUID,
    ForeignKey("users.id", ondelete="SET NULL"),  # Preserve records
    nullable=True,
    index=True
)
```

#### Migration Validation Script
Create `scripts/validate_migrations.py`:
```python
def validate_models():
    """Pre-migration validation checks."""
    # 1. Import all models
    from app.db.models import Base, User, RefreshToken

    # 2. Check foreign key indexes
    for table in Base.metadata.tables.values():
        fk_columns = {fk.parent.name for fk in table.foreign_keys}
        indexed_columns = {col.name for idx in table.indexes for col in idx.columns}

        missing = fk_columns - indexed_columns
        if missing:
            raise ValueError(f"Missing indexes on {table.name}: {missing}")

    # 3. Verify no circular dependencies
    # 4. Check naming conventions
    print("✅ All migration checks passed!")
```

#### Alembic Configuration
```python
# alembic/env.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.models import Base  # Import all models via Base

# Use settings for database URL
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
target_metadata = Base.metadata
```

#### Common Migration Pitfalls
- **Missing FK indexes**: Always create indexes on foreign key columns
- **UUID defaults**: Use `default=uuid.uuid4` not `default=str(uuid.uuid4())`
- **Timezone issues**: Always use `DateTime(timezone=True)`
- **Import order**: Ensure all models are imported in `db/models/__init__.py`
- **Async driver**: Use `postgresql+asyncpg://` for async SQLAlchemy

---

## 5. Security Implementation

### JWT Token Structure
```python
# Access Token Claims
{
    "sub": "user_id",          # Subject (user ID)
    "exp": 1234567890,         # Expiration (15 minutes)
    "iat": 1234567890,         # Issued at
    "type": "access",          # Token type
    "jti": "unique_token_id"   # JWT ID
}

# Refresh Token Claims
{
    "sub": "user_id",
    "exp": 1234567890,         # Expiration (30 days)
    "iat": 1234567890,
    "type": "refresh",
    "jti": "unique_token_id"
}
```

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- Bcrypt hashing with 12 rounds

### Rate Limiting
- Login attempts: 5 per 15 minutes (by email + IP)
- Registration: 10 per IP per day
- API requests (authenticated): 1000 per hour
- API requests (unauthenticated): 100 per hour

### Security Headers
```python
# FastAPI middleware
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 6. Testing Patterns

### Environment-First Testing Setup

**CRITICAL**: Set up the complete testing environment before writing any tests. This prevents the cascade of fixes that come from environment mismatches.

#### Pre-Testing Environment Audit
```bash
# 1. Dependency Audit - Run this FIRST
pip freeze > current_requirements.txt
diff requirements-dev.txt current_requirements.txt

# 2. Code Structure Audit - Understand before extending
find src/ -name "*.py" -exec grep -l "class.*Exception" {} \;
find src/ -name "*.py" -exec grep -l "def get_current_user" {} \;
find tests/ -name "*.py" -exec grep -l "AsyncClient" {} \;

# 3. Test Patterns Audit - Follow existing patterns
pytest tests/ --collect-only | head -20  # See test structure
grep -r "pytest.fixture" tests/ | head -5  # See fixture patterns

# 4. Version Compatibility Check
python -c "import httpx; print('httpx version:', httpx.__version__)"
python -c "from httpx import AsyncClient, ASGITransport"  # Test imports
```

#### Environment Setup Verification
```bash
# Install all dependencies upfront
pip install -r requirements-dev.txt

# Verify async database support
python -c "from sqlalchemy.ext.asyncio import create_async_engine; print('✅ Async SQLAlchemy ready')"
python -c "import asyncpg; print('✅ AsyncPG ready')"

# Verify test tooling
python -c "import pytest, faker, httpx; print('✅ Test tools ready')"

# Set correct PYTHONPATH for imports
export PYTHONPATH=/path/to/project/src
python -c "from app.api.main import app; print('✅ App imports work')"
```

#### "One Shot" Testing Philosophy
Instead of the traditional "implement then fix" cycle:

1. **Read First**: Understand existing code patterns and signatures
2. **Environment Check**: Verify all dependencies and versions
3. **Pattern Match**: Follow existing test structures exactly
4. **Test Small**: Write one test, verify it works, then continue
5. **Validate Continuously**: Run tests after each addition

> **Implementation Note**: See IMPLEMENTATION_PLAN.md "Phase 0: Environment Audit" for the complete step-by-step checklist to implement this philosophy.

### Test Categories
- **Unit Tests** (60% of tests): Individual functions and methods
- **Integration Tests** (30% of tests): Module interactions and API endpoints
- **Functional Tests** (10% of tests): End-to-end scenarios

### Coverage Requirements & Strategy
- Overall: 80% minimum (MANDATORY - not negotiable)
- Core business logic: 90% minimum
- API endpoints: 85% minimum
- Security functions: 95% minimum

#### 80% Coverage Achievement Strategy

**CRITICAL**: 80% is not a suggestion - it's a hard requirement. Use this systematic approach to reach it:

##### 1. Coverage Analysis Workflow
```bash
# Get current coverage with detailed report
pytest --cov=src --cov-report=html --cov-report=term-missing
# Open htmlcov/index.html to see exactly which lines need coverage

# Identify priority modules (highest impact for coverage gain)
pytest --cov=src --cov-report=term | grep -E "TOTAL|src/" | sort -k4 -nr
```

##### 2. Module-by-Module Coverage Strategy

**High-Impact Modules** (focus here first for biggest coverage gains):
- `src/app/api/routes/` - Usually 200+ lines, often <30% covered
- `src/app/core/` - Core business logic, easier to test
- `src/app/api/dependencies.py` - Critical auth functions

**Medium-Impact Modules**:
- `src/app/db/models/` - Model properties and methods
- `src/app/api/middleware/` - Request/response processing

**Low-Priority for Coverage** (exclude or test minimally):
- `src/app/cli/` - CLI commands
- `src/app/core/config_production.py` - Production-only code
- Migration scripts

##### 3. Systematic Testing Approach

**Step 1: Unit Test All Core Functions (40-50% coverage)**
```bash
# Test every function in these modules:
pytest --cov=src/app/core --cov-report=term-missing
# Aim for 95%+ coverage in core modules
```

**Step 2: Integration Test All API Endpoints (70-75% coverage)**
```bash
# Test every endpoint with success/error cases:
pytest --cov=src/app/api/routes --cov-report=term-missing
# Each route needs: success case, validation error, auth error
```

**Step 3: Test Remaining Components (80%+ coverage)**
```bash
# Cover middleware, dependencies, utilities:
pytest --cov=src --cov-report=term-missing
# Focus on modules still showing red in HTML report
```

##### 4. Coverage Verification Commands

```bash
# MANDATORY: Run this before claiming phase complete
pytest --cov=src --cov-report=term --cov-fail-under=80
# This command MUST pass - if it fails, phase is not complete

# Generate HTML report for line-by-line analysis
pytest --cov=src --cov-report=html
echo "Open htmlcov/index.html to see uncovered lines"

# Focus on specific modules if needed
pytest tests/unit/test_auth.py --cov=src/app/api/routes/auth --cov-report=term-missing
```

##### 5. Common Coverage Gaps & Solutions

**Gap**: Low API route coverage (20-30%)
**Solution**: Test each endpoint with all scenarios:
```python
# For each endpoint, test:
- Success case with valid data
- Validation error (422)
- Authentication required (401)
- Authorization denied (403)
- Resource not found (404)
- Rate limiting (429)
```

**Gap**: Untested error handling paths
**Solution**: Force error conditions:
```python
# Test exception handling
with patch('module.function', side_effect=Exception("Database error")):
    response = client.post("/api/endpoint")
    assert response.status_code == 500
```

**Gap**: Missing model method tests
**Solution**: Test all model properties and methods:
```python
# Test model properties, relationships, custom methods
user = User(email="test@example.com")
assert user.is_active == True
assert user.full_name == "Test User"
```

##### 6. Coverage Automation

Add to pytest.ini:
```ini
[tool:pytest]
addopts = --cov=src --cov-fail-under=80 --cov-report=term-missing
```

This ensures every test run validates the 80% requirement.

### Complete System Verification

After implementing all components, run this comprehensive verification to ensure everything works:

#### Full Stack Health Check
```bash
# 1. Environment Setup
export PYTHONPATH=$(pwd)/src
source venv/bin/activate  # or your virtual environment

# 2. Install all dependencies
pip install -r requirements-dev.txt
cd ui && npm install && cd ..

# 3. Database setup (if using Docker)
docker-compose up -d db
sleep 10  # Wait for database to be ready

# 4. Run database migrations
make migrate

# 5. Backend verification
echo "🔍 Testing backend..."
make test                    # All tests pass
make lint                    # No linting errors
make type-check             # No type errors
pytest --cov=src --cov-fail-under=80  # Coverage requirement met

# 6. Frontend verification
echo "🔍 Testing frontend..."
cd ui
npm test                    # All tests pass
npm run lint               # No linting errors
npm run type-check         # No TypeScript errors
npm run build              # Build succeeds
cd ..

# 7. Integration verification
echo "🔍 Testing full stack..."
docker-compose up -d       # Start all services
sleep 30                   # Wait for services

# Test API endpoints
curl -f http://localhost:8000/health || echo "❌ API health check failed"
curl -f http://localhost:3000 || echo "❌ Frontend not accessible"

# Test auth flow
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"TestPass123!"}' \
  || echo "❌ Registration endpoint failed"

# 8. Cleanup
docker-compose down

echo "✅ Full stack verification complete!"
```

#### Continuous Integration Simulation
```bash
# Simulate what CI will run
echo "🤖 Running CI simulation..."

# Backend CI pipeline
make format              # Format all code
make lint               # Check code style
make type-check         # Verify types
make test-cov           # Run tests with coverage
make security-check     # Security analysis

# Frontend CI pipeline
cd ui
npm run format          # Format code
npm run lint           # Check style
npm run type-check     # Verify TypeScript
npm test -- --coverage # Test with coverage
npm run build          # Production build
cd ..

# Integration CI pipeline
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
docker-compose -f docker-compose.test.yml down

echo "✅ CI simulation passed!"
```

### Test Fixtures
```python
# User fixtures
@pytest.fixture
async def test_user(test_db):
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    return user

# Auth fixtures
@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

# Database fixtures
@pytest.fixture
async def test_db():
    async with AsyncSession() as session:
        yield session
        await session.rollback()
```

### Backend Testing Stack
- pytest with async support
- pytest-cov for coverage
- httpx for API testing
- faker for test data generation

### Frontend Testing Stack
- Vitest with jsdom environment
- React Testing Library
- @vitest/coverage-v8 for coverage
- MSW (Mock Service Worker) for API mocking

### Frontend Testing Patterns

#### Component Testing
```typescript
// Test setup with providers
export function renderWithProviders(
  ui: React.ReactElement,
  options?: RenderOptions
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        <App>{children}</App>
      </BrowserRouter>
    );
  }
  return render(ui, { wrapper: Wrapper, ...options });
}

// Third-party UI component testing
it('shows loading spinner', () => {
  render(<AuthGuard><div>Protected</div></AuthGuard>);
  // Don't assume ARIA roles - query by actual attributes
  const spinner = document.querySelector('[aria-busy="true"]');
  expect(spinner).toBeInTheDocument();
});
```

#### Store Testing
```typescript
// Zustand store testing
beforeEach(() => {
  // Reset store state
  useAuthStore.setState({ user: null, token: null });
  // Clear all mocks
  vi.clearAllMocks();
});

// Handle act() warnings - they're expected
it('updates user state', async () => {
  const { result } = renderHook(() => useAuthStore());
  // act() warnings here are normal - document them
  await act(async () => {
    result.current.setUser(mockUser);
  });
  expect(result.current.user).toEqual(mockUser);
});
```

#### Mock Management
```typescript
// React Router mocks
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Navigate: vi.fn(() => null), // Returns null, not JSX
    useNavigate: vi.fn(() => mockNavigate),
  };
});

// Component prop expectations
expect(Navigate).toHaveBeenCalledWith(
  { to: '/login', replace: true },
  undefined // React passes undefined, not {}
);
```

### Testing Best Practices & Common Pitfalls

#### Dependencies & Environment Setup
- **Async PostgreSQL**: When using SQLAlchemy with async, include `asyncpg` in requirements
  ```python
  # requirements.txt
  sqlalchemy>=2.0.23
  asyncpg>=0.29.0  # Required for async PostgreSQL
  psycopg2-binary>=2.9.9  # Keep for migrations/compatibility
  ```

- **Test Environment Configuration**: Always create `.env.test` upfront
  ```bash
  # Initial setup
  cp .env.example .env.test
  # Update DATABASE_URL to use test database
  # Set TESTING=1
  ```

- **Database URL Schemes**: Use correct scheme for async
  ```python
  # For async SQLAlchemy
  postgresql+asyncpg://user:pass@host/db  # NOT just postgresql://
  ```

#### Modern Python Patterns
- Avoid deprecated methods:
  ```python
  # Old (deprecated in Python 3.12+)
  datetime.utcnow()

  # New
  from datetime import timezone
  datetime.now(timezone.utc)
  ```

#### Test-Implementation Alignment
- Write tests and implementation together to avoid mismatches
- Run tests immediately after implementation
- Use TDD when possible to ensure alignment
- When importing functions in tests, ensure they exist in implementation

#### Test Organization
- Structure tests for easy execution:
  ```bash
  # Run only unit tests (no DB required)
  pytest tests/unit/ -v

  # Run integration tests separately (requires DB)
  pytest tests/integration/ -v
  ```

#### Coverage Strategy
- Set realistic initial goals:
  ```ini
  # pytest.ini
  [coverage:run]
  omit =
      */tests/*
      */migrations/*
      */config_production.py  # Exclude production-only files

  [coverage:report]
  fail_under = 70  # Start with achievable goal, increase over time
  ```

### Frontend Testing Best Practices & Common Pitfalls

#### Dependencies & Setup
- **Testing Stack**: Include all required dependencies upfront
  ```json
  // package.json
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.0.0",
    "@vitest/coverage-v8": "^1.0.0",  // Critical for coverage
    "jsdom": "^23.0.0",
    "vitest": "^1.0.0"
  }
  ```

- **Vitest Configuration**: Complete setup from the start
  ```typescript
  // vitest.config.ts
  export default defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
      css: {
        modules: {
          classNameStrategy: 'non-scoped'
        }
      },
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        thresholds: {
          branches: 50,    // Start realistic
          functions: 50,
          lines: 50,
          statements: 50
        }
      }
    }
  });
  ```

#### Third-Party UI Component Testing
- **DOM Inspection**: Don't assume ARIA roles for third-party components
  ```typescript
  // ❌ Wrong: Assuming Ant Design spinner has role="img"
  expect(screen.getByRole('img')).toBeInTheDocument();

  // ✅ Correct: Query by actual DOM attributes
  const spinner = document.querySelector('[aria-busy="true"]');
  expect(spinner).toHaveClass('ant-spin-spinning');
  ```

- **Flexible Queries**: Use multiple query strategies
  ```typescript
  // Strategy 1: Class names for UI libraries
  const modal = document.querySelector('.ant-modal');

  // Strategy 2: Text content
  expect(screen.getByText('Loading...')).toBeInTheDocument();

  // Strategy 3: Test IDs for critical elements
  expect(screen.getByTestId('auth-guard-spinner')).toBeInTheDocument();
  ```

#### React Testing Patterns
- **Mock Signatures**: React components receive undefined, not empty objects
  ```typescript
  // ❌ Wrong expectation
  expect(Navigate).toHaveBeenCalledWith({ to: '/login' }, {});

  // ✅ Correct expectation
  expect(Navigate).toHaveBeenCalledWith({ to: '/login' }, undefined);
  ```

- **Mock Cleanup**: Always clean mocks to prevent test interference
  ```typescript
  beforeEach(() => {
    vi.clearAllMocks();  // Critical for test isolation
  });
  ```

- **Complete Props**: When expecting component calls, include all props
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

#### Store Testing Considerations
- **State Reset**: Reset store state before each test
  ```typescript
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isLoading: false
    });
  });
  ```

- **Act Warnings**: Expected for Zustand - document them
  ```typescript
  // This will show act() warnings - that's normal
  const { result } = renderHook(() => useAuthStore());
  ```

#### Coverage Strategies
- **Realistic Goals**: Start with achievable coverage
  ```json
  // package.json
  "test:coverage": "vitest --coverage",
  "coverage": {
    "branches": 50,    // Increase gradually
    "functions": 50,   // As codebase matures
    "lines": 50,
    "statements": 50
  }
  ```

- **Exclude Patterns**: Focus on testable code
  ```typescript
  // vitest.config.ts
  coverage: {
    exclude: [
      'node_modules',
      'dist',
      '**/*.d.ts',
      '**/*.config.*',
      '**/mockServiceWorker.js',
      'src/main.tsx'  // Entry points
    ]
  }
  ```

#### Mock Management
- **Clean Mocks Between Tests**: Prevent test interference
  ```typescript
  describe('Component', () => {
    beforeEach(() => {
      vi.clearAllMocks();  // Essential for test isolation
    });
  });
  ```

- **Mock React Router Correctly**: Match actual React behavior
  ```typescript
  // ❌ Wrong: Navigate doesn't receive empty object
  expect(Navigate).toHaveBeenCalledWith(
    { to: '/login' },
    {}  // React passes undefined, not {}
  );

  // ✅ Correct: Match actual call signature
  expect(Navigate).toHaveBeenCalledWith(
    { to: '/login', replace: true },
    undefined
  );
  ```

#### Store Testing Patterns
- **Zustand Store Testing**: Handle act() warnings properly
  ```typescript
  import { renderHook, act } from '@testing-library/react';

  describe('Auth Store', () => {
    beforeEach(() => {
      // Reset store state before each test
      useAuthStore.setState({
        user: null,
        tokens: null,
        isAuthenticated: false
      });
    });

    it('should handle async actions', async () => {
      const { result } = renderHook(() => useAuthStore());

      // Note: act() warnings are expected and normal
      await act(async () => {
        await result.current.login({ email: 'test@test.com', password: 'pass' });
      });

      expect(result.current.isAuthenticated).toBe(true);
    });
  });
  ```

#### Test Utils Setup
- **Enhanced Test Utils**: Include all providers and mocks
  ```typescript
  // src/test/utils.tsx
  import { render as rtlRender } from '@testing-library/react';
  import { MemoryRouter } from 'react-router-dom';
  import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

  // Mock router from the start
  vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
      ...actual,
      Navigate: vi.fn(() => null),
      useNavigate: () => vi.fn()
    };
  });

  export function render(ui: React.ReactElement, options = {}) {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });

    return rtlRender(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          {ui}
        </MemoryRouter>
      </QueryClientProvider>,
      options
    );
  }
  ```

#### Frontend Test Organization
```
ui/src/
├── components/
│   ├── AuthGuard.tsx
│   └── AuthGuard.test.tsx      # Co-locate tests
├── stores/
│   ├── authStore.ts
│   └── authStore.test.ts       # Store tests
├── utils/
│   ├── validation.ts
│   └── validation.test.ts      # Utility tests
└── test/
    ├── setup.ts                # Global test setup
    ├── utils.tsx               # Test utilities
    └── mocks/                  # Shared mocks
        └── handlers.ts         # MSW handlers
```

---

## 7. Deployment Structure

### Docker Configuration
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/appdb
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  frontend:
    build:
      context: ./ui
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - frontend

volumes:
  postgres_data:
```

### Environment Variables
```bash
# Required
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional
REDIS_URL=redis://localhost:6379/0
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@example.com
SMTP_PASSWORD=smtp-password
FRONTEND_URL=https://app.example.com

# Development
DEBUG=0
TESTING=0

# Performance
MAX_WORKERS=4
CONNECTION_POOL_SIZE=20
CACHE_TTL=300
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] Redis cache configured (optional)
- [ ] Email service configured
- [ ] Monitoring/logging setup
- [ ] Backup strategy implemented
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] CORS properly configured

---

## 8. Implementation Completion Criteria

### Definition of Done
A full-stack template implementation is **NOT COMPLETE** until all phases are finished:

#### Core Application (Phases 1-9)
- [ ] Backend API fully functional with auth endpoints
- [ ] Frontend application with login/register/dashboard
- [ ] Database migrations tested and working
- [ ] All tests passing (backend + frontend)
- [ ] Linting and type checking passing
- [ ] Docker deployment verified
- [ ] Documentation updated

#### Client SDKs (Phase 10) - REQUIRED
- [ ] Python SDK package created with:
  - Authentication methods (login, register, refresh)
  - Type hints for all methods
  - Error handling
  - Usage examples
  - Published to PyPI or internal registry
- [ ] TypeScript SDK package created with:
  - Full TypeScript types
  - Promise-based API
  - Automatic token refresh
  - Error types
  - Published to npm or internal registry

### Why Client SDKs Matter
Without SDKs, developers must:
- Write raw HTTP requests
- Handle authentication manually
- Parse responses without type safety
- Implement token refresh logic repeatedly

With SDKs, developers can:
```python
# Python SDK usage
from your_api import Client
client = Client(base_url="https://api.example.com")
user = client.auth.login(username="user", password="pass")
```

```typescript
// TypeScript SDK usage
import { ApiClient } from '@your-org/api-client';
const client = new ApiClient({ baseUrl: 'https://api.example.com' });
const user = await client.auth.login({ username: 'user', password: 'pass' });
```

---

## 8. WBS Framework Patterns

### Master Template WBS
```aispec
Feature: FullStackTemplate {
  What:
    - "Production-ready full-stack application template"
    - "JWT-based authentication system"
    - "User management with registration and login"
    - "RESTful API with FastAPI backend"
    - "React frontend with TypeScript"
    - "PostgreSQL database with migrations"

  Boundaries:
    # Performance
    - "API response time: <200ms for auth endpoints"
    - "Frontend bundle size: <500KB"
    - "Database query time: <50ms"

    # Security
    - "JWT expiry: 15 minutes access, 30 days refresh"
    - "Password: 8+ chars with complexity"
    - "Rate limiting: 5 login attempts per 15 minutes"

    # Scale
    - "Concurrent users: 1000 maximum"
    - "Database connections: 20 pool size"

  Success:
    - "All auth endpoints functional"
    - "Frontend routing with auth guards"
    - "80% test coverage minimum"
    - "Docker deployment ready"
    - "Security best practices implemented"
}
```

### Component-Level WBS Example
```aispec
Component: UserAuthentication {
  What:
    - "Handle user login and token generation"
    - "Validate credentials against database"
    - "Generate JWT tokens on success"

  Boundaries:
    - "Response time: <100ms"
    - "Max login attempts: 5 per 15 minutes"
    - "Token size: <1KB"

  Success:
    - "Valid users receive tokens"
    - "Invalid attempts are logged"
    - "Rate limiting enforced"
}
```

---

## 9. Development Workflow

### Continuous Quality Assurance

**CRITICAL**: Quality checks must be integrated throughout development, not just at the end.

#### After Every Code Change
Run these commands before moving to the next task:
```bash
# Backend changes
make test              # Run tests immediately
make lint              # Check code style
make type-check        # Verify type annotations

# Frontend changes
npm test              # Run tests immediately
npm run lint          # Check code style
npx tsc --noEmit      # Verify TypeScript types
```

#### Before Every Commit
1. **Format all code**:
   ```bash
   make format           # Runs black, isort, prettier
   ```

2. **Run full validation**:
   ```bash
   make test-all         # All tests must pass
   make lint             # No linting errors
   make type-check       # No type errors
   ```

3. **Check coverage**:
   ```bash
   make test-cov         # Verify coverage thresholds
   ```

#### Quality Gates
- ❌ **Never commit** with failing tests
- ❌ **Never commit** with linting errors
- ❌ **Never commit** with type errors
- ❌ **Never skip** quality checks to "save time"

#### Common Quality Issues to Prevent

1. **Test-Implementation Mismatch**
   - Write tests alongside implementation
   - Run tests immediately after code changes
   - Update tests when changing implementations

2. **Missing Type Annotations**
   ```python
   # ❌ Bad
   def get_user(id):
       return db.query(User).get(id)

   # ✅ Good
   def get_user(id: str) -> Optional[User]:
       return db.query(User).get(id)
   ```

3. **Inconsistent Formatting**
   - Configure your editor to format on save
   - Run formatters before committing
   - Use pre-commit hooks

4. **Low Test Coverage**
   - Write tests for all new functions
   - Test both success and error paths
   - Don't skip edge cases

---

## 9. Development Workflow (Original)

### Git Workflow
```bash
# Branch naming
feature/add-user-preferences
bugfix/fix-token-validation
hotfix/security-patch

# Commit message format
type(scope): description

# Types: feat, fix, docs, style, refactor, test, chore
# Example: feat(auth): add password reset flow
```

### Pre-commit Hooks
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
```

### Code Quality & Linting Best Practices

#### Backend Linting Configuration
```ini
# pyproject.toml - Unified Python tooling config
[tool.black]
line-length = 88
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.tox
  | venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = E203, E266, W503  # Black compatibility
exclude = .git,__pycache__,migrations,venv

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true
```

#### Frontend Linting Configuration
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_",
      "caughtErrors": "none"
    }]
  },
  "overrides": [{
    "files": ["*.test.ts", "*.test.tsx", "src/test/**/*"],
    "rules": {
      "react-refresh/only-export-components": "off"
    }
  }]
}
```

#### Common Linting Pitfalls & Solutions

**Backend Issues:**
- **Unused imports**: Remove immediately after refactoring
- **Exception handling**: Don't capture variables you won't use
  ```python
  # ❌ Bad
  except Exception as e:
      raise CustomError("Failed")

  # ✅ Good
  except Exception:
      raise CustomError("Failed")
  ```
- **Boolean comparisons**: Use proper checks
  ```python
  # ❌ Bad
  if value == True:

  # ✅ Good
  if value:
  # For SQLAlchemy
  if value is True:
  ```

**Frontend Issues:**
- **Type safety**: Avoid `any` types
  ```typescript
  // ❌ Bad
  } as any);

  // ✅ Good
  } as ReturnType<typeof useStore>);
  ```
- **Test utilities**: Add ESLint exception
  ```typescript
  /* eslint-disable react-refresh/only-export-components */
  ```

#### Linting Workflow
1. **Format first**: `black src/` (Python) or `prettier --write .` (JS/TS)
2. **Fix imports**: `isort src/` (Python)
3. **Run linters**: `flake8 src/` and `npm run lint`
4. **Type check**: `mypy src/` and `npm run type-check`

### Type Checking Best Practices

#### Python Type Annotations
```python
# types.py - Common type aliases
from typing import Any, Dict, Optional, Union, Callable, TypeVar
from fastapi import Request as FastAPIRequest

# Type aliases for cleaner code
JSONDict = Dict[str, Any]
OptionalDict = Optional[Dict[str, Any]]
AnyCallable = Callable[..., Any]
AsyncFunc = Callable[..., Awaitable[Any]]
```

#### Essential Imports
```python
# Always import these at the top of modules
from typing import (
    Any, Dict, List, Optional, Union,
    Callable, TypeVar, Generic, Tuple,
    Awaitable, cast
)
```

#### Common Type Patterns

**Request Parameters**
```python
# ❌ Untyped
def get_client_ip(request) -> str:
    return request.client.host

# ✅ Typed
def get_client_ip(request: Any) -> str:  # or FastAPIRequest
    return str(request.client.host) if request.client else "unknown"
```

**Optional Parameters**
```python
# ❌ Implicit Optional (no longer allowed)
def process(data: Dict[str, Any] = None):
    pass

# ✅ Explicit Optional
def process(data: Optional[Dict[str, Any]] = None) -> None:
    pass
```

**Pydantic v2 Validators**
```python
from pydantic import field_validator, ValidationInfo

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_db_url(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if v:
            return v
        # Access other fields via info.data
        values = info.data
        return f"postgresql://{values.get('DB_USER')}..."
```

**SQLAlchemy Patterns**
```python
# Column comparisons
query.filter(Model.active == True)  # noqa: E712

# Model base class
class Base(DeclarativeBase):
    id: Any  # Avoid type issues

    @declared_attr  # type: ignore[misc]
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
```

**Return Type Conversions**
```python
# ❌ Implicit Any return
def get_token() -> str:
    return jwt.encode(payload, key)  # Returns Any

# ✅ Explicit conversion
def get_token() -> str:
    return str(jwt.encode(payload, key))
```

**Callable Types**
```python
# ❌ Unparameterized
def decorator(func: Callable) -> Callable:
    pass

# ✅ Parameterized
def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    pass

# ✅ More specific
def cache(func: Callable[[int], str]) -> Callable[[int], str]:
    pass
```

#### Mypy Configuration
```ini
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true
no_implicit_optional = true  # Python 3.10+ default

# Gradual typing per module
[[tool.mypy.overrides]]
module = "app.api.routes.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
ignore_errors = true
```

#### Common Type Checking Issues & Solutions

**Library Return Types**
- Problem: External libraries often return `Any`
- Solution: Explicitly cast or convert returns
```python
result = str(external_lib.function())
data = cast(Dict[str, Any], json.loads(response))
```

**Click CLI Commands**
```python
@click.command()
def init_db() -> None:  # Always return None
    """Initialize database."""
    click.echo("Initializing...")
```

**Async Function Types**
```python
async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    # For dependency injection
    return data

# Type alias for cleaner signatures
AsyncProcessor = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
```

### CI/CD Pipeline
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: pip install -e ".[dev]"
      - run: make lint
      - run: make test-cov
      - run: make security-check
```

### Makefile Commands
```makefile
# Development
install-dev:    # Install with dev dependencies
serve-api:      # Run development server
test:           # Run tests
test-cov:       # Run with coverage
lint:           # Run all linters
format:         # Format code

# Production
build:          # Build for production

# Database
migrate:        # Run database migrations
migrate-create: # Create new migration (validates first)
migrate-down:   # Rollback last migration
migrate-validate: # Validate models before migration

# Docker
docker-build:   # Build Docker image
docker-up:      # Start services
docker-down:    # Stop services
```

---

## 10. Client SDKs Pattern

### Python SDK Structure
```python
class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-API-Key": api_key} if api_key else {},
            timeout=30.0
        )

        # Sub-clients
        self.auth = AuthClient(self.client)
        self.users = UsersClient(self.client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()
```

### TypeScript SDK Structure
```typescript
export class APIClient {
  private client: AxiosInstance;
  public auth: AuthClient;
  public users: UsersClient;

  constructor(config: ClientConfig) {
    this.client = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout || 30000,
      headers: {
        'X-API-Key': config.apiKey,
        'Content-Type': 'application/json',
      },
    });

    // Initialize sub-clients
    this.auth = new AuthClient(this.client);
    this.users = new UsersClient(this.client);
  }
}
```

---

## 11. Common Utilities

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
)

# Usage
logger.info(
    "user_login",
    user_id=user.id,
    ip_address=request.client.host,
    success=True
)
```

### In-Memory Cache with LRU
```python
from functools import lru_cache
import time

class CacheManager:
    def __init__(self, max_size: int = 1000):
        self._storage: Dict[str, CacheEntry] = {}
        self.max_size = max_size

    def cached(self, ttl: Optional[int] = None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, *args, **kwargs)

                # Check cache
                if cached_value := self.get(key):
                    return cached_value

                # Execute function
                result = func(*args, **kwargs)

                # Cache result
                self.set(key, result, ttl)
                return result

            return wrapper
        return decorator
```

### Email Service
```python
async def send_email(
    to: str,
    subject: str,
    html: str,
    from_email: Optional[str] = None
):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_email or SMTP_USER
    message["To"] = to

    part = MIMEText(html, "html")
    message.attach(part)

    async with aiosmtplib.SMTP(
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        use_tls=True
    ) as smtp:
        await smtp.login(SMTP_USER, SMTP_PASSWORD)
        await smtp.send_message(message)
```

### Monitoring Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)
```

---

## 12. Project Structure Template

```
project_name/
├── src/app_name/
│   ├── api/                      # FastAPI application
│   │   ├── routes/               # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   └── users.py         # User management endpoints
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── main.py              # FastAPI app setup
│   │   └── schemas.py           # Pydantic schemas
│   ├── core/                     # Business logic
│   │   ├── __init__.py
│   │   ├── config.py            # Settings management
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── security.py          # JWT and password handling
│   │   └── cache.py             # Caching logic
│   ├── db/                       # Database layer
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model
│   │   │   └── base.py          # Base models
│   │   ├── session.py           # Database session
│   │   └── init_db.py           # Database initialization
│   └── cli/                      # CLI commands
│       └── commands.py          # Click commands
├── ui/                           # React frontend
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── components/          # Reusable components
│   │   │   ├── AuthGuard.tsx
│   │   │   └── Layout.tsx
│   │   ├── stores/              # Zustand stores
│   │   │   └── authStore.ts
│   │   ├── services/            # API services
│   │   │   └── api.ts
│   │   ├── types/               # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── client-sdk/                   # Client libraries
│   ├── python/                   # Python SDK
│   │   ├── src/
│   │   ├── setup.py
│   │   └── requirements.txt
│   └── typescript/               # TypeScript SDK
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── functional/               # End-to-end tests
│   └── conftest.py              # Pytest configuration
├── scripts/                      # Utility scripts
│   ├── lint.py                  # Linting orchestrator
│   └── setup_dev.sh             # Development setup
├── docker/                       # Docker configurations
│   ├── Dockerfile               # API container
│   ├── Dockerfile.frontend      # UI container
│   └── docker-compose.yml       # Full stack
├── alembic/                      # Database migrations
│   ├── versions/
│   └── alembic.ini
├── .github/                      # GitHub Actions
│   └── workflows/
│       └── ci.yml               # CI pipeline
├── .env.example                  # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml      # Pre-commit hooks
├── Makefile                     # Common commands
├── pyproject.toml               # Python project config
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── README.md                    # Project documentation
└── pytest.ini                   # Pytest configuration
```

---

## Summary

This template provides a solid foundation for any full-stack application with:
- Complete authentication system with JWT tokens
- Modern tech stack (FastAPI + React + TypeScript)
- Production-ready security implementation
- Comprehensive testing setup
- Docker deployment configuration
- Development best practices and tooling
- Extensible architecture for adding features

The template follows the WBS framework principles, ensuring clear boundaries and measurable success criteria for each component.
