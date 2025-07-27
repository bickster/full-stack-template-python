# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main components:

1. **AISpec Framework** - A specification language for AI-first development implementing the What-Boundaries-Success (WBS) framework
2. **Full-Stack Template** - A production-ready template for building applications with authentication, based on CORE_FULLSTACK_TEMPLATE.md

## Key Concepts

### AISpec and WBS Framework
- **AISpec Format**: Define features using What (objectives), Boundaries (constraints), and Success (criteria)
- **Bora's Law**: I = Bi(C²) - Intelligence scales with constraints, not compute
- **Intent Engineering**: Focus on defining clear constraints rather than implementation details

### Full-Stack Template Architecture
- **Backend**: FastAPI with JWT authentication, SQLAlchemy ORM, PostgreSQL
- **Frontend**: React 18 + TypeScript + Vite, Zustand for state, Ant Design UI
- **Authentication**: JWT tokens (15min access, 30day refresh), rate limiting, bcrypt hashing
- **Deployment**: Docker + Docker Compose + nginx

## Common Development Tasks

### Working with AISpec Files
```bash
# AISpec files use .aispec extension
# Example structure:
Feature: FeatureName {
  What:
    - "Clear objectives"
  Boundaries:
    - "Constraints"
  Success:
    - "Measurable outcomes"
}
```

### Full-Stack Template Implementation

#### Phase Execution Guide
When implementing the full-stack template, **ALL 10 PHASES** must be completed:

**Phase Tracking:**
1. Use the Implementation Tracking Checklist in IMPLEMENTATION_PLAN.md
2. Complete phases sequentially - each builds on the previous
3. Don't skip Phase 10 (Client SDKs) - it's part of the complete template

**Phase Overview:**
- Phase 1-2: Project foundation and database setup
- Phase 3-4: Backend core and authentication API  
- Phase 5-6: Frontend foundation and auth features
- Phase 7: Testing setup (often reveals issues - don't skip!)
- Phase 8: Code quality tools (linting, type checking)
- Phase 9: Production deployment readiness
- Phase 10: **Client SDKs** (Python & TypeScript) - Essential for API consumption

**Implementation Commands:**
```bash
# After each phase, verify completion:
make test         # All tests passing
make lint         # No linting errors  
make type-check   # No type errors
make build        # Docker builds successfully

# Phase 10 specific:
cd client-sdk/python && python setup.py sdist
cd client-sdk/typescript && npm run build
```

**Common Pitfall:** Stopping after Phase 9 because "it works". The client SDKs in Phase 10 are crucial for other applications to easily consume your API.

## Architecture Patterns

### Backend Structure (FastAPI)
- **Dependency Injection**: Use FastAPI's dependency system for auth and database sessions
- **Pydantic Schemas**: Define request/response models for type safety
- **JWT Implementation**: Access tokens (15min) and refresh tokens (30days) with proper validation
- **Rate Limiting**: Implement on auth endpoints (5 attempts per 15 minutes)

### Frontend Structure (React)
- **Auth Store**: Zustand store managing user state and tokens
- **Protected Routes**: Wrap components requiring authentication
- **Axios Interceptors**: Handle token refresh automatically
- **Form Validation**: react-hook-form + zod for type-safe forms

### Database Schema
Key tables for authentication:
- `users`: Core user data with soft delete support
- `refresh_tokens`: Token management with revocation
- `login_attempts`: Track failed logins for rate limiting
- `audit_logs`: Security and compliance logging

## Testing Strategy
- **Coverage Requirements**: 80% overall, 90% business logic, 95% security functions
- **Test Categories**: Unit (60%), Integration (30%), Functional (10%)
- **Backend**: pytest with async support and fixtures
- **Frontend**: Jest/Vitest for component and store testing

## Security Considerations
- **Password Requirements**: 8+ chars with complexity rules, bcrypt (12 rounds)
- **Token Security**: Short-lived access tokens, secure refresh token storage
- **Rate Limiting**: Implement on all auth endpoints
- **Security Headers**: X-Frame-Options, CSP, HSTS, etc.
- **Audit Logging**: Track all authentication events

## Performance Targets
- API response time: <200ms for auth endpoints
- Frontend bundle size: <500KB
- Database query time: <50ms
- Support for 1000 concurrent users

## Docker Deployment
- Multi-stage builds for optimization
- Separate containers for API, frontend, database, nginx
- Environment-specific configurations
- Health checks and monitoring setup