# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main components:

1. **AISpec Framework** - A specification language for AI-first development implementing the What-Boundaries-Success (WBS) framework
2. **Full-Stack Template** - A production-ready template for building applications with authentication, based on CORE_FULLSTACK_TEMPLATE.md

## Critical Implementation Principles

### Configuration Management First

One of the most common issues in full-stack development is configuration mismatches between frontend and backend. Test these immediately after setup:

#### Environment Variable Hierarchy
1. **Check .env files first** - They override default values in code
2. **Common override issue**:
   ```javascript
   // src/services/api.ts
   baseURL: import.meta.env.VITE_API_URL || '/api/v1'  // .env value wins!
   ```
3. **Solution**: When using proxies, ensure .env uses relative paths:
   ```bash
   # .env - CORRECT for proxy setup
   VITE_API_URL=/api/v1

   # .env - WRONG (causes CORS)
   VITE_API_URL=http://localhost:8000/api/v1
   ```

#### Testing Configuration Early
```bash
# After initial setup
curl http://localhost:3000  # Frontend loads?
curl http://localhost:8000/health  # Backend running?

# Test API integration immediately
# Try registration/login - don't wait until Phase 6!
```

#### Common CORS Issues
- **Symptom**: "Access to XMLHttpRequest blocked by CORS policy"
- **Cause**: Frontend using full URL instead of proxy
- **Debug**: Check Network tab - is request going to localhost:8000 or localhost:3000/api?
- **Fix**: Use relative URLs and configure proxy in vite.config.ts

### Quality-First Development

**The Golden Rule**: "Environment first, then test as you code, not after you code"

#### After Every Code Change
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
```bash
make format           # Format all code
make test-all         # All tests must pass
make lint             # No linting errors
make type-check       # No type errors
```

### Testing Philosophy

1. **Test Early**: Run tests immediately after implementation
2. **Test Together**: Write tests alongside code, not after
3. **Environment First**: Complete environment audit before writing tests
4. **Coverage Requirements**: 80% minimum (mandatory, not negotiable)

## Phase Execution Quick Reference

### Phase Verification Commands

**Phase 1-2 (Foundation & Database)**:
```bash
pre-commit run --all-files  # All hooks pass
make migrate-check          # No pending changes
make migrate-up && make migrate-down  # Migrations work
```

**Phase 3-4 (Backend Core & Auth)**:
```bash
pytest tests/integration/test_auth_*.py -v  # Auth tests pass
make test-cov -- src/app/api/routes/auth.py # >80% coverage
curl -X POST localhost:8000/api/v1/auth/register  # Endpoint responds
```

**Phase 5-6 (Frontend)**:
```bash
cd ui && npm test && npm run lint && npm run type-check
# Verify no CORS errors in browser console
```

**Phase 7 (Testing)**:
```bash
pytest --cov=src --cov-fail-under=80  # MUST pass
```

**Phase 8-10 (Quality & Deployment)**:
```bash
make lint && make type-check && make test-cov
docker-compose build && docker-compose up
```

## Common Pitfalls by Phase

### Configuration Issues
- **Frontend can't connect to backend**: Check .env for full URLs vs relative paths
- **CORS errors**: Verify proxy configuration in vite.config.ts
- **Environment variables not working**: .env files override code defaults

### Database Issues
- **Async driver error**: Use `postgresql+asyncpg://` not just `postgresql://`
- **Missing indexes on foreign keys**: Always index FK columns
- **UUID defaults**: Use `default=uuid.uuid4` not `default=str(uuid.uuid4())`

### Testing Issues
- **Import errors**: Write tests alongside implementation
- **Coverage failing**: Start with 70%, exclude non-critical files
- **Frontend component testing**: Query by actual DOM attributes for third-party UI

### Type Checking
- **Build fails but dev works**: Run `npm run build` every 30-60 minutes
- **Type errors accumulating**: Use `npm run dev:all` for real-time checking
- **Import type errors**: Use `import type` for type-only imports

## Key Architecture Patterns

### Backend (FastAPI)
- **Dependency Injection**: Use FastAPI's dependency system
- **Async Throughout**: Use asyncpg for database
- **JWT Tokens**: Access (15min) + Refresh (30days)
- **Rate Limiting**: 5 login attempts per 15 minutes

### Frontend (React + TypeScript)
- **Zustand State**: Simple, type-safe state management
- **Protected Routes**: AuthGuard component pattern
- **Axios Interceptors**: Automatic token refresh
- **Vite Proxy**: Development API integration

### Testing Strategy
- **Backend**: pytest with async support, 80% coverage
- **Frontend**: Vitest with realistic goals (start 50%)
- **Integration**: Test all auth endpoints with all scenarios

## Development Commands

### Essential Make Commands
```bash
make install-dev    # Install with dev dependencies
make test          # Run tests
make test-cov      # Run with coverage (must be 80%+)
make lint          # Run all linters
make format        # Format code
make type-check    # Type checking
make migrate       # Run migrations
make build         # Build for production
```

### TypeScript Development
```bash
npm run dev:all    # Dev server + type checking
npm run build      # Build (run every 30-60 mins)
npm run check-all  # Before committing
```

## References to Detailed Guides

- **Full Implementation Details**: See [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)
- **Complete Architecture**: See [CORE_FULLSTACK_TEMPLATE.md](docs/CORE_FULLSTACK_TEMPLATE.md)
- **Testing Setup**: See [TESTING_GUIDE.md](docs/guides/TESTING_GUIDE.md)
- **API Integration**: See [API_INTEGRATION.md](docs/guides/API_INTEGRATION.md)
- **Authentication**: See [AUTHENTICATION_GUIDE.md](docs/guides/AUTHENTICATION_GUIDE.md)
- **Deployment**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md) and [DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)

## Important Reminders

- **Phase 10 (Client SDKs) is REQUIRED** - Don't stop at Phase 9
- **Always run quality checks** before committing
- **Test configuration immediately** after setup
- **Fix type errors as they occur**, not at build time
- **80% test coverage is mandatory**, not optional

---

For detailed information on any topic, refer to the guides linked above. This file focuses on critical patterns and common issues you'll encounter during implementation.
