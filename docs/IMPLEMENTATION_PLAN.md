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
4. **MANDATORY for Phase 7**: `pytest --cov=src --cov-fail-under=80` passes
5. Documentation is updated
6. Changes are committed to version control

### Phase 7 Specific Verification
```bash
# These commands MUST all pass before Phase 7 is complete:
pytest --cov=src --cov-fail-under=80                    # 80% coverage achieved
pytest tests/integration/test_auth_complete.py -v       # All auth endpoints tested
pytest tests/unit/test_security.py --cov-fail-under=95  # Security 95% covered
make lint && make type-check                             # Code quality maintained
```

### Quality Checkpoints Per Phase

**IMPORTANT**: Run these checks after EVERY file you create or modify:

#### Backend File Changes
```bash
# After creating/modifying any Python file:
python -m py_compile path/to/file.py  # Syntax check
make test                              # Run relevant tests
make lint                              # Fix any style issues
make type-check                        # Add missing annotations
```

#### Frontend File Changes
```bash
# After creating/modifying any TypeScript file:
npx tsc --noEmit path/to/file.tsx    # Type check single file
npm test -- --run --reporter=dot      # Quick test run
npm run lint -- --fix                  # Auto-fix issues
```

#### Database Changes
```bash
# After modifying models:
make migrate-check                     # Verify migration needed
make migrate-create MSG="description"  # Create migration
make migrate-up                        # Test migration
make migrate-down                      # Test rollback
make migrate-up                        # Re-apply
```

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
11. **CRITICAL: Configure frontend proxy and test immediately**:
    - Set up vite.config.ts proxy for /api routes
    - Create frontend .env with `VITE_API_URL=/api/v1` (relative path)
    - Test that frontend can load: `curl http://localhost:3000`
    - Verify proxy setup in browser DevTools Network tab

**✓ Phase 1 Quality Gate:**
```bash
# Must pass before proceeding to Phase 2:
pre-commit run --all-files  # All hooks pass
make install-dev            # All dependencies installed
make lint                   # No errors (empty src is OK)
docker-compose config       # Valid Docker config
```

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

**✓ Phase 2 Quality Gate:**
```bash
# Must pass before proceeding to Phase 3:
python -c "from app.db.models import *"  # All models importable
make migrate-check                        # No pending changes
make migrate-up && make migrate-down      # Migrations work both ways
pytest tests/unit/test_models.py -v       # Model tests pass
mypy src/app/db/ --strict                 # Type checks pass
```

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

**✓ Phase 4 Quality Gate:**
```bash
# Must pass before proceeding to Phase 5:
pytest tests/integration/test_auth_*.py -v  # All auth tests pass
make test-cov -- src/app/api/routes/auth.py # >80% coverage
curl -X POST localhost:8000/api/v1/auth/register  # Endpoint responds
python scripts/test_rate_limiting.py        # Rate limits work
black src/app/api/ --check                 # Properly formatted
```

### Phase 5: Frontend Foundation (Days 11-13)
1. Set up React Router v6
2. Configure Axios with interceptors
3. Create auth store with Zustand
4. Implement protected route component
5. Set up form validation (react-hook-form + zod)
6. Configure TailwindCSS and Ant Design
7. Create layout components
8. **CRITICAL: Test API integration immediately**:
   - Verify API client uses relative URLs
   - Check that .env doesn't override with full URLs
   - Test a simple API call (even just to /health)
   - Confirm no CORS errors in browser console

### Phase 6: Frontend Auth Features (Days 14-16)
1. Create login page with form validation
2. Create registration page
3. Implement dashboard (protected)
4. Add logout functionality
5. Handle token refresh automatically
6. Create error boundary
7. Add loading states and error handling

### Phase 7: Testing Setup (Days 17-19)

**BEFORE STARTING**: Complete the Environment Audit from "Continuous Quality Practices" section above. This prevents most testing issues.

1. Backend testing:
   - **Environment Setup** (use audit checklist above):
     - Verify all dependencies installed (asyncpg, pytest, faker, httpx)
     - Set PYTHONPATH correctly for imports
     - Check httpx version compatibility (ASGITransport vs app parameter)
   - **Code Discovery** (understand before extending):
     - Read existing function signatures before writing tests
     - Check actual exception class names (AppException vs APIException)
     - Understand existing test fixture patterns
   - **Incremental Implementation**:
     - Create .env.test with test database configuration
     - Ensure test database URL uses postgresql+asyncpg://
     - Create test fixtures (user, auth, database) following existing patterns
     - Write ONE test file at a time, verify it works before continuing
     - Write unit tests for security functions
     - Write integration tests for auth endpoints
     - **MANDATORY: Achieve exactly 80% coverage using systematic approach below**
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

## Continuous Quality Practices

> **Note**: For quality-first development principles and the environment audit checklist, see [CLAUDE.md](../CLAUDE.md#quality-first-development).

### Quality Indicators
- ✅ Every function has a test
- ✅ Every endpoint has integration tests
- ✅ Every module has type hints
- ✅ Coverage stays above threshold
- ✅ Zero linting warnings

## Configuration Troubleshooting Guide

> **Note**: For common configuration issues and solutions, see [CLAUDE.md](../CLAUDE.md#configuration-issues).

For additional configuration troubleshooting not covered in CLAUDE.md:

## Common Testing Pitfalls & Solutions

> **Note**: For testing issues and solutions, see [CLAUDE.md](../CLAUDE.md#testing-issues).

For detailed testing setup and additional issues not covered in CLAUDE.md, see [TESTING_GUIDE.md](guides/TESTING_GUIDE.md).

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
- 80% overall coverage (MANDATORY - see detailed strategy below)
- 90% coverage for business logic
- 95% coverage for security functions
- All auth endpoints tested
- E2E tests for critical flows

## 80% Coverage Achievement Plan

**CRITICAL**: Phase 7 is NOT complete until you achieve exactly 80% coverage. Use this step-by-step plan:

### Step 1: Setup Coverage Automation (Day 17)

```bash
# 1. Configure pytest to enforce 80% coverage
cat >> pytest.ini << 'EOF'
[tool:pytest]
addopts = --cov=src --cov-fail-under=80 --cov-report=html --cov-report=term-missing
omit =
    */tests/*
    */migrations/*
    */config_production.py
    */cli/commands.py
EOF

# 2. Install coverage HTML reporting
pip install coverage[toml]

# 3. Verify baseline coverage
pytest --cov=src --cov-report=term
echo "📊 Current coverage recorded - target is 80%"
```

### Step 2: Core Module Testing (Target: 50% overall coverage)

```bash
# Test all core modules to 95%+ coverage
pytest tests/unit/test_security.py --cov=src/app/core/security --cov-report=term-missing
pytest tests/unit/test_exceptions.py --cov=src/app/core/exceptions --cov-report=term-missing
pytest tests/unit/test_utils.py --cov=src/app/core/utils --cov-report=term-missing

# Verify core coverage
pytest --cov=src/app/core --cov-report=term-missing
echo "🎯 Core modules should show 90%+ coverage"
```

### Step 3: API Routes Testing (Target: 75% overall coverage)

**Critical**: API routes have the most lines of code. Focus here for biggest coverage gains.

```bash
# 3a. Create comprehensive auth route tests
touch tests/integration/test_auth_complete.py
```

Add this test file content:
```python
"""Comprehensive auth endpoint testing for 80% coverage."""

class TestAuthEndpointsComplete:

    # For EACH endpoint, test ALL scenarios:

    # POST /api/v1/auth/register
    async def test_register_success(self, client): pass  # 201
    async def test_register_duplicate_email(self, client): pass  # 409
    async def test_register_duplicate_username(self, client): pass  # 409
    async def test_register_weak_password(self, client): pass  # 422
    async def test_register_invalid_email(self, client): pass  # 422
    async def test_register_missing_fields(self, client): pass  # 422

    # POST /api/v1/auth/login
    async def test_login_success(self, client): pass  # 200
    async def test_login_wrong_password(self, client): pass  # 401
    async def test_login_nonexistent_user(self, client): pass  # 401
    async def test_login_inactive_user(self, client): pass  # 401
    async def test_login_rate_limited(self, client): pass  # 429
    async def test_login_missing_fields(self, client): pass  # 422

    # POST /api/v1/auth/refresh
    async def test_refresh_success(self, client): pass  # 200
    async def test_refresh_invalid_token(self, client): pass  # 401
    async def test_refresh_expired_token(self, client): pass  # 401
    async def test_refresh_revoked_token(self, client): pass  # 401
    async def test_refresh_malformed_token(self, client): pass  # 401

    # POST /api/v1/auth/logout
    async def test_logout_success(self, client): pass  # 200
    async def test_logout_invalid_token(self, client): pass  # 401
    async def test_logout_already_logged_out(self, client): pass  # 401

    # GET /api/v1/users/me
    async def test_get_profile_success(self, client): pass  # 200
    async def test_get_profile_unauthorized(self, client): pass  # 401

    # PUT /api/v1/users/me
    async def test_update_profile_success(self, client): pass  # 200
    async def test_update_duplicate_email(self, client): pass  # 409
    async def test_update_invalid_data(self, client): pass  # 422
    async def test_update_unauthorized(self, client): pass  # 401

    # DELETE /api/v1/users/me
    async def test_delete_account_success(self, client): pass  # 200
    async def test_delete_wrong_password(self, client): pass  # 401
    async def test_delete_unauthorized(self, client): pass  # 401
```

```bash
# 3b. Implement all the test methods above
echo "📝 Implement each test method to cover success/error paths"

# 3c. Verify API coverage
pytest tests/integration/test_auth_complete.py --cov=src/app/api/routes --cov-report=term-missing
echo "🎯 API routes should show 80%+ coverage"
```

### Step 4: Dependencies and Middleware (Target: 80% overall coverage)

```bash
# 4a. Test all dependency functions
pytest tests/unit/test_dependencies.py --cov=src/app/api/dependencies --cov-report=term-missing

# 4b. Create middleware tests
touch tests/unit/test_middleware.py
```

Add middleware test content:
```python
"""Test middleware components for coverage."""

class TestSecurityMiddleware:
    async def test_security_headers_added(self): pass
    async def test_cors_headers_added(self): pass
    async def test_rate_limiting_enforced(self): pass

class TestVersioningMiddleware:
    async def test_api_version_extraction(self): pass
    async def test_version_validation(self): pass
```

### Step 5: Coverage Verification and Completion

```bash
# 5a. Run full coverage check
pytest --cov=src --cov-report=html --cov-report=term
echo "📊 Check coverage percentage in terminal output"

# 5b. Generate detailed HTML report
echo "🌐 Open htmlcov/index.html to see line-by-line coverage"

# 5c. MANDATORY: Verify 80% threshold
pytest --cov=src --cov-fail-under=80
# This command MUST pass before proceeding to Phase 8

# 5d. Coverage by module analysis
pytest --cov=src --cov-report=term | grep -E "(Name|TOTAL|src/)" | tail -20
echo "📋 Review modules below 80% and add targeted tests"
```

### Step 6: If Coverage Is Still Below 80%

```bash
# Identify specific uncovered lines
pytest --cov=src --cov-report=term-missing | grep "Missing"

# Focus on highest-impact modules
pytest --cov=src --cov-report=term | grep "src/app" | sort -k4 -nr | head -5

# Add targeted tests for uncovered lines
echo "🎯 Add specific tests for uncovered code paths"
```

### Coverage Success Criteria

✅ **Phase 7 Complete When**:
- `pytest --cov=src --cov-fail-under=80` passes
- HTML coverage report shows 80%+ overall
- All critical auth endpoints have tests
- Core security functions have 95%+ coverage
- No untested error handling paths in auth routes

❌ **Phase 7 NOT Complete Until**:
- Coverage reaches exactly 80% or higher
- All auth endpoints tested with success/error cases
- Security functions fully tested

## Complete System Verification

**CRITICAL**: Run these verification steps after each major phase and before considering the project complete.

### Daily Development Verification (Run After Each Code Change)

```bash
# Quick health check (2-3 minutes)
export PYTHONPATH=$(pwd)/src

# Backend quick check
make test-unit          # Unit tests only (fast)
make lint              # Linting check
pytest tests/unit/test_security.py -v  # Critical security tests

# Frontend quick check
cd ui && npm test -- --run --reporter=dot && cd ..

echo "✅ Daily verification complete"
```

### Phase Completion Verification (Run After Each Phase)

```bash
# Complete phase verification (10-15 minutes)
echo "🔍 Running phase completion verification..."

# 1. Environment setup
export PYTHONPATH=$(pwd)/src
source venv/bin/activate

# 2. Full backend verification
echo "🔧 Backend verification..."
make install-dev        # All dependencies installed
make test              # All tests pass
make lint              # No linting errors
make type-check        # No type errors
pytest --cov=src --cov-fail-under=80  # Coverage meets requirement

# 3. Database verification
echo "🗄️ Database verification..."
docker-compose up -d db
sleep 10
make migrate           # Migrations work
make migrate-down      # Rollback works
make migrate-up        # Re-apply works

# 4. API verification
echo "🌐 API verification..."
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 10

# Test critical endpoints
curl -f http://localhost:8000/health || echo "❌ Health endpoint failed"
curl -f http://localhost:8000/api/v1/docs || echo "❌ API docs failed"

# Test auth endpoints
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"verify@test.com","username":"verify","password":"VerifyPass123!"}' \
  && echo "✅ Registration works" || echo "❌ Registration failed"

kill $API_PID

# 5. Frontend verification (if Phase 5+ complete)
if [ -d "ui" ]; then
  echo "🖥️ Frontend verification..."
  cd ui
  npm install            # Dependencies installed
  npm test              # All tests pass
  npm run lint          # No linting errors
  npm run type-check    # No type errors
  npm run build         # Build succeeds
  cd ..
fi

echo "✅ Phase verification complete!"
```

### Complete Project Verification (Run Before Project Handoff)

```bash
# Full system integration test (20-30 minutes)
echo "🚀 Running complete project verification..."

# 1. Clean environment setup
export PYTHONPATH=$(pwd)/src
source venv/bin/activate

# 2. Full dependency verification
echo "📦 Verifying all dependencies..."
pip install -r requirements-dev.txt
cd ui && npm install && cd ..

# 3. Database integration test
echo "🗄️ Database integration test..."
docker-compose down -v  # Clean slate
docker-compose up -d db
sleep 15
make migrate
make test-integration   # Integration tests

# 4. Full stack integration test
echo "🌐 Full stack integration test..."
docker-compose up -d
sleep 30

# Wait for services to be ready
for i in {1..30}; do
  curl -f http://localhost:8000/health >/dev/null 2>&1 && break
  echo "Waiting for API... ($i/30)"
  sleep 2
done

for i in {1..30}; do
  curl -f http://localhost:3000 >/dev/null 2>&1 && break
  echo "Waiting for frontend... ($i/30)"
  sleep 2
done

# 5. End-to-end auth flow test
echo "🔐 Testing complete auth flow..."

# Register user
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"e2e@test.com","username":"e2euser","password":"E2ETest123!"}')

echo "Registration response: $REGISTER_RESPONSE"

# Login user
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e@test.com","password":"E2ETest123!"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token' 2>/dev/null || echo "")

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo "✅ Login successful, token received"

  # Test authenticated endpoint
  PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/users/me)

  echo "Profile response: $PROFILE_RESPONSE"

  if echo $PROFILE_RESPONSE | grep -q "e2e@test.com"; then
    echo "✅ Authenticated endpoint works"
  else
    echo "❌ Authenticated endpoint failed"
  fi
else
  echo "❌ Login failed or no token received"
fi

# 6. Performance verification
echo "⚡ Performance verification..."
echo "Testing API response time..."
time curl -s http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e@test.com","password":"E2ETest123!"}'

# 7. Security verification
echo "🔒 Security verification..."
# Test rate limiting
echo "Testing rate limiting..."
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"nonexistent@test.com","password":"wrong"}' \
    | grep -q "429" && echo "✅ Rate limiting active" && break
done

# Test security headers
echo "Testing security headers..."
curl -I http://localhost:8000/ | grep -q "X-Frame-Options" && echo "✅ Security headers present"

# 8. Code quality verification
echo "📊 Code quality verification..."
make test-cov           # Full test suite with coverage
make lint              # All linting passes
make type-check        # All type checking passes
make security-check    # Security analysis passes

# 9. Build verification
echo "🏗️ Build verification..."
cd ui && npm run build && cd ..
docker-compose -f docker-compose.prod.yml build

# 10. Cleanup
docker-compose down -v

echo "🎉 COMPLETE PROJECT VERIFICATION PASSED!"
echo "Project is ready for deployment and handoff."
```

### Quick Smoke Test (Run Anytime)

```bash
# 2-minute smoke test to verify nothing is broken
export PYTHONPATH=$(pwd)/src

# Critical path test
pytest tests/unit/test_security.py::TestPasswordHashing::test_get_password_hash -v
pytest tests/unit/test_security.py::TestTokenCreation::test_create_access_token -v

# API smoke test
docker-compose up -d db api
sleep 15
curl -f http://localhost:8000/health && echo "✅ API healthy"
docker-compose down

echo "✅ Smoke test passed"
```

### Verification Schedule

**During Development:**
- Run "Daily Development Verification" after each code session
- Run "Quick Smoke Test" before committing changes

**After Each Phase:**
- Run "Phase Completion Verification" before marking phase complete
- Fix any issues before proceeding to next phase

**Before Project Handoff:**
- Run "Complete Project Verification"
- All checks must pass before considering project complete

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
