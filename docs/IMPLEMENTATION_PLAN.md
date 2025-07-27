# Full-Stack Application Template Implementation Plan

## Overview
Implement a production-ready full-stack application based on CORE_FULLSTACK_TEMPLATE.md with JWT authentication, FastAPI backend, React frontend, PostgreSQL database, and Docker deployment.

## Implementation Tracking Checklist

**IMPORTANT**: Use this checklist to ensure all phases are completed. Each phase builds on the previous ones and should not be skipped.

- [x] Phase 1: Project Foundation
- [x] Phase 2: Database & Models  
- [x] Phase 3: Backend Core & Security
- [x] Phase 4: Authentication API
- [x] Phase 5: Frontend Foundation
- [x] Phase 6: Frontend Auth Features
- [x] Phase 7: Testing Setup
- [x] Phase 8: Development Tools & Code Quality
- [x] Phase 9: Production Deployment
- [x] Phase 10: Client SDKs & Documentation ✅ **COMPLETED!**

### Verification Gates
Before marking a phase complete, ensure:
1. All items in the phase are implemented
2. Code passes linting and type checking
3. Tests are written and passing
4. Documentation is updated
5. Changes are committed to version control

## Technology Stack
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy, Alembic
- **Frontend**: React 18, TypeScript, Vite, Zustand, Ant Design, TailwindCSS
- **Database**: PostgreSQL 15
- **Authentication**: JWT with access/refresh tokens
- **Testing**: pytest (backend), Jest/Vitest (frontend)
- **Deployment**: Docker, Docker Compose, nginx

## Implementation Phases

### Phase 1: Project Foundation (Days 1-2)
1. Create project structure following the template
2. Initialize git repository
3. Set up Python virtual environment
4. Create backend package structure (src/app_name/)
5. Initialize frontend with Vite + React + TypeScript
6. Set up Docker and docker-compose.yml
7. Create .env.example with all required variables
8. Configure pre-commit hooks and linting:
   - Create pyproject.toml with Black, isort, flake8, mypy configs
   - Create .eslintrc.json with TypeScript and React rules
   - Install and configure pre-commit hooks
   - Run initial formatting: `black src/` and `prettier --write .`
9. Create test environment configuration (.env.test)
10. Ensure async dependencies are included (asyncpg for PostgreSQL)

### Phase 2: Database & Models (Days 3-4)
1. Set up PostgreSQL with Docker
2. Configure SQLAlchemy with async support (postgresql+asyncpg://)
3. Create base model with proper patterns:
   - UUID with callable defaults: `default=uuid.uuid4`
   - Timezone-aware timestamps: `DateTime(timezone=True)`
   - Automatic created_at/updated_at with `server_default=func.now()`
4. Create models with proper indexes:
   - User model with indexes on email, username, is_active
   - RefreshToken with indexes on token_hash, user_id (FK)
   - LoginAttempt with indexes on email, ip, user_id (FK)
   - AuditLog with composite indexes for queries
5. Set up Alembic for migrations:
   - Configure env.py to use app settings
   - Add all models to db/models/__init__.py
   - Create validation script before first migration
6. Validate and create initial migration:
   - Run scripts/validate_migrations.py
   - Check all foreign keys have indexes
   - Verify ON DELETE behaviors
   - Generate migration with proper naming
7. Implement database initialization scripts

### Phase 3: Backend Core & Security (Days 5-7)
1. Implement core configuration (settings.py)
2. Create security module:
   - Password hashing (bcrypt, 12 rounds)
   - JWT token generation (access: 15min, refresh: 30days)
   - Token validation and refresh logic
   - Use timezone-aware datetime (datetime.now(timezone.utc))
3. Create custom exceptions
4. Implement rate limiting logic
5. Set up structured logging
6. Create cache manager

### Phase 4: Authentication API (Days 8-10)
1. Create auth endpoints:
   - POST /register (with email validation)
   - POST /login (with attempt tracking)
   - POST /refresh (token refresh)
   - POST /logout (token revocation)
   - GET /me (user profile)
   - DELETE /me (account deletion)
2. Implement dependency injection for auth
3. Create Pydantic schemas for requests/responses
4. Add security headers middleware
5. Configure CORS

### Phase 5: Frontend Foundation (Days 11-13)
1. Set up React Router v6
2. Configure Axios with interceptors
3. Create auth store with Zustand
4. Implement protected route component
5. Set up form validation (react-hook-form + zod)
6. Configure TailwindCSS and Ant Design
7. Create layout components

### Phase 6: Frontend Auth Features (Days 14-16)
1. Create login page with form validation
2. Create registration page
3. Implement dashboard (protected)
4. Add logout functionality
5. Handle token refresh automatically
6. Create error boundary
7. Add loading states and error handling

### Phase 7: Testing Setup (Days 17-19)
1. Backend testing:
   - Set up pytest with async support
   - Create .env.test with test database configuration
   - Install async database driver (asyncpg)
   - Ensure test database URL uses postgresql+asyncpg://
   - Create test fixtures (user, auth, database)
   - Write unit tests for security functions
   - Write integration tests for auth endpoints
   - Run tests immediately to catch implementation mismatches
   - Achieve 80%+ coverage (consider excluding production-only files)
2. Frontend testing:
   - Configure Vitest with jsdom environment
   - Install all testing dependencies upfront (@vitest/coverage-v8, @testing-library/react, etc.)
   - Create test setup file with global mocks
   - Set up enhanced test utils with all providers
   - Mock react-router-dom properly (Navigate returns null, passes undefined as second arg)
   - Test auth store with proper state reset in beforeEach
   - Test protected routes (AuthGuard) with flexible DOM queries for third-party UI components
   - Test API interceptors with proper mock cleanup
   - Handle Zustand act() warnings (they're expected and normal)
   - Start with realistic coverage goals (50%, increase over time)

### Phase 8: Development Tools & Code Quality (Days 20-21)
1. Configure linting and formatting tools:
   - Backend: Black, isort, flake8, mypy with pyproject.toml
   - Frontend: ESLint, Prettier with proper TypeScript rules
   - Set up pre-commit hooks for automatic formatting
2. Configure type checking:
   - Create types.py with common type aliases
   - Set up mypy with strict settings and gradual typing
   - Add type annotations to all core modules
   - Configure pydantic v2 validators with ValidationInfo
3. Create Makefile with all commands including:
   - `make format`: Run Black and Prettier
   - `make lint`: Run all linters
   - `make type-check`: Run mypy and tsc
4. Set up GitHub Actions CI/CD pipeline with linting and type checks
5. Configure monitoring (Prometheus metrics)
6. Add email service (password reset ready)
7. Create development setup scripts
8. Write comprehensive README with linting and type checking guidelines

### Phase 9: Production Deployment (Days 22-23)
1. Create production Dockerfiles (multi-stage)
2. Configure nginx reverse proxy
3. Set up SSL certificate handling
4. Create production docker-compose
5. Add health check endpoints
6. Configure environment-specific settings
7. Create deployment checklist

### Phase 10: Client SDKs & Documentation (Days 24-25)
1. Create Python SDK package
2. Create TypeScript SDK package
3. Generate API documentation
4. Create usage examples
5. Write deployment guide
6. Create troubleshooting guide

## Common Testing Pitfalls & Solutions

### Database Configuration
- **Issue**: Tests fail with "The asyncio extension requires an async driver"
- **Solution**: Use `asyncpg` and `postgresql+asyncpg://` URL scheme

### Test-Implementation Mismatch
- **Issue**: Tests expect different behavior than implementation provides
- **Solution**: Write tests alongside implementation or use TDD

### Missing Dependencies
- **Issue**: Runtime errors due to missing async drivers
- **Solution**: Include all async dependencies in requirements.txt from the start

### Environment Setup
- **Issue**: Tests fail due to missing configuration
- **Solution**: Create .env.test as part of initial setup

### Coverage Requirements
- **Issue**: Tests pass but coverage fails
- **Solution**: 
  - Set realistic initial coverage goals (70% to start)
  - Exclude production-only files from coverage
  - Focus on critical paths first

### Modern Python Compatibility
- **Issue**: Deprecation warnings with datetime.utcnow()
- **Solution**: Use `datetime.now(timezone.utc)` for Python 3.12+ compatibility

### Frontend Testing: Third-Party UI Components
- **Issue**: Tests fail looking for ARIA roles that don't exist (e.g., Ant Design Spin)
- **Solution**: Query by actual DOM attributes (`document.querySelector('[aria-busy="true"]')`)

### Frontend Testing: React Router Mocks
- **Issue**: Navigate mock expectations fail with wrong arguments
- **Solution**: React passes `undefined` not `{}` as second argument to components

### Frontend Testing: Mock State Persistence
- **Issue**: Tests interfere with each other due to mock state
- **Solution**: Always use `vi.clearAllMocks()` in `beforeEach`

### Frontend Testing: Zustand Store Warnings
- **Issue**: act() warnings when testing stores
- **Solution**: These warnings are expected and normal - document them

### Frontend Testing: Coverage Dependencies
- **Issue**: Coverage command fails with missing dependency
- **Solution**: Install `@vitest/coverage-v8` from the start

## Common Linting & Code Quality Issues

### Backend Linting: Format Conflicts
- **Issue**: Black and flake8 disagree on formatting
- **Solution**: Configure flake8 to ignore Black's style choices
  ```ini
  [flake8]
  max-line-length = 88
  extend-ignore = E203, E266, W503
  ```

### Backend Linting: Import Organization
- **Issue**: Import order conflicts between isort and Black
- **Solution**: Configure isort to use Black profile
  ```ini
  [tool.isort]
  profile = "black"
  ```

### Frontend Linting: Any Types in Tests
- **Issue**: Test mocks trigger no-explicit-any errors
- **Solution**: Use proper return types
  ```typescript
  // Instead of: as any
  as ReturnType<typeof useAuthStore>
  ```

### Frontend Linting: Unused Catch Variables
- **Issue**: ESLint complains about unused error variables
- **Solution**: Use anonymous catch blocks when error isn't needed
  ```typescript
  try {
    await someAction();
  } catch {  // No variable
    // Handle error
  }
  ```

### Pre-commit Hook Setup
- **Issue**: Linting issues discovered after commit
- **Solution**: Install pre-commit hooks from day one
  ```bash
  pip install pre-commit
  pre-commit install
  pre-commit run --all-files  # Initial check
  ```

## Common Database Migration Issues

### Missing Foreign Key Indexes
- **Issue**: Poor query performance on joins
- **Solution**: Always index foreign key columns
  ```python
  __table_args__ = (
      Index("idx_table_user_id", "user_id"),  # FK index
  )
  ```

### UUID Default Values
- **Issue**: Same UUID for all records when using string default
- **Solution**: Use callable, not executed function
  ```python
  # ❌ Wrong
  id = Column(UUID, default=str(uuid.uuid4()))
  
  # ✅ Correct
  id = Column(UUID, default=uuid.uuid4)
  ```

### Model Import Failures
- **Issue**: Models not found by Alembic autogenerate
- **Solution**: Import all models in db/models/__init__.py
  ```python
  from .base import Base
  from .user import User
  from .refresh_token import RefreshToken
  # Import all models to register with Base.metadata
  ```

### Async Driver Configuration
- **Issue**: "The asyncio extension requires an async driver"
- **Solution**: Use correct connection string
  ```python
  DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
  ```

### Migration Validation
- **Issue**: Discovering model issues after migration creation
- **Solution**: Validate before creating migrations
  ```bash
  python scripts/validate_migrations.py
  make migrate-create MSG="initial schema"
  ```

## Key Implementation Details

### Security Measures
- JWT tokens with proper expiration
- Password complexity validation
- Rate limiting on auth endpoints
- Secure password storage (bcrypt)
- CORS configuration
- Security headers
- Audit logging

### Performance Targets
- API response time: <200ms
- Frontend bundle: <500KB
- Database queries: <50ms
- 1000 concurrent users support

### Testing Requirements
- 80% overall coverage
- 90% coverage for business logic
- 95% coverage for security functions
- All auth endpoints tested
- E2E tests for critical flows

## Deliverables
1. Complete source code with clean architecture
2. Docker deployment ready
3. Comprehensive test suite
4. API and deployment documentation
5. Client SDKs (Python & TypeScript)
6. Pre-configured development environment
7. CI/CD pipeline
8. Production deployment guide

## Success Criteria
- All auth endpoints functional
- Frontend routing with auth guards working
- 80%+ test coverage achieved
- Docker deployment successful
- Security best practices implemented
- Performance targets met
- Documentation complete

## Project Structure
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