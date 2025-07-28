# API Versioning Strategy

This document outlines the versioning strategy for the FullStack API, ensuring backward compatibility and smooth transitions for API consumers.

## Table of Contents
1. [Versioning Principles](#versioning-principles)
2. [Versioning Scheme](#versioning-scheme)
3. [Implementation](#implementation)
4. [Breaking Changes](#breaking-changes)
5. [Deprecation Policy](#deprecation-policy)
6. [Client Migration Guide](#client-migration-guide)
7. [Version Support Matrix](#version-support-matrix)

## Versioning Principles

### Core Principles
1. **Backward Compatibility**: Existing clients continue to work without modification
2. **Clear Communication**: Version changes are well-documented and communicated
3. **Graceful Migration**: Provide migration paths and adequate time for transitions
4. **Semantic Versioning**: Follow semantic versioning principles for clarity

### Goals
- Minimize disruption to existing integrations
- Enable API evolution and improvement
- Maintain multiple versions simultaneously when needed
- Provide clear upgrade paths

## Versioning Scheme

### URL Path Versioning
We use URL path versioning for major versions:
```
https://api.example.com/api/v1/users
https://api.example.com/api/v2/users
```

### Version Format
- **Major Version**: Breaking changes (v1, v2, v3)
- **Minor Version**: New features, backward compatible (1.1, 1.2)
- **Patch Version**: Bug fixes (1.1.1, 1.1.2)

### Header-Based Minor Versioning
Minor versions can be requested via header:
```
X-API-Version: 1.2
```

## Implementation

### Current Implementation

```python
# src/app/core/config.py
API_V1_STR = "/api/v1"
API_V2_STR = "/api/v2"  # Future version

# src/app/api/main.py
app.include_router(auth_v1.router, prefix=API_V1_STR)
app.include_router(users_v1.router, prefix=API_V1_STR)

# Future: v2 routers
# app.include_router(auth_v2.router, prefix=API_V2_STR)
```

### Version Detection Middleware

```python
# src/app/api/middleware/versioning.py
from fastapi import Request, HTTPException
from typing import Optional

class VersioningMiddleware:
    """Handle API versioning through headers and paths."""

    SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2"]
    DEFAULT_VERSION = "1.0"

    async def __call__(self, request: Request, call_next):
        # Extract version from header
        header_version = request.headers.get("X-API-Version")

        # Extract version from path
        path_parts = request.url.path.split("/")
        path_version = None
        if len(path_parts) > 2 and path_parts[2].startswith("v"):
            path_version = path_parts[2][1:]  # Remove 'v' prefix

        # Determine final version
        version = header_version or f"{path_version}.0" if path_version else self.DEFAULT_VERSION

        # Validate version
        if version not in self.SUPPORTED_VERSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported API version: {version}"
            )

        # Store version in request state
        request.state.api_version = version

        response = await call_next(request)

        # Add version headers to response
        response.headers["X-API-Version"] = version
        response.headers["X-API-Deprecated"] = "false"

        return response
```

### Conditional Response Fields

```python
# src/app/api/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional

class UserResponse(BaseModel):
    """User response with version-specific fields."""

    # Common fields (all versions)
    id: str
    username: str
    email: str

    # v1.0+ fields
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # v1.1+ fields
    full_name: Optional[str] = None
    is_verified: bool = False

    # v1.2+ fields
    last_login: Optional[datetime] = None
    preferences: Optional[dict] = None

    @classmethod
    def from_orm_versioned(cls, obj, version: str):
        """Create response based on API version."""
        data = {
            "id": str(obj.id),
            "username": obj.username,
            "email": obj.email,
            "is_active": obj.is_active,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }

        if version >= "1.1":
            data["full_name"] = obj.full_name
            data["is_verified"] = obj.is_verified

        if version >= "1.2":
            data["last_login"] = obj.last_login
            data["preferences"] = obj.preferences

        return cls(**data)
```

### Version-Specific Endpoints

```python
# src/app/api/v1/routes/users.py
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_v1(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current user (v1 endpoint)."""
    version = getattr(request.state, "api_version", "1.0")
    return UserResponse.from_orm_versioned(current_user, version)

# src/app/api/v2/routes/users.py (future)
@router.get("/users/me", response_model=UserResponseV2)
async def get_current_user_v2(
    current_user: User = Depends(get_current_user),
    include_stats: bool = False
):
    """Get current user with optional statistics (v2 endpoint)."""
    response = UserResponseV2.from_orm(current_user)

    if include_stats:
        response.stats = await get_user_stats(current_user.id)

    return response
```

## Breaking Changes

### What Constitutes a Breaking Change

1. **Removing endpoints**
2. **Removing or renaming response fields**
3. **Changing field types** (string to number)
4. **Changing authentication methods**
5. **Modifying request/response formats**
6. **Changing error codes or formats**

### What is NOT a Breaking Change

1. **Adding new endpoints**
2. **Adding optional request parameters**
3. **Adding response fields**
4. **Adding new error codes**
5. **Performance improvements**
6. **Bug fixes that don't change behavior**

### Breaking Change Process

1. **Announcement**: 6 months before deprecation
2. **Beta Release**: New version available for testing
3. **Dual Support**: Both versions supported simultaneously
4. **Migration Period**: 12 months minimum
5. **Sunset**: Old version deprecated with notice

## Deprecation Policy

### Deprecation Timeline

```
v1.0 Released        : January 2024
v2.0 Announced       : July 2024      (6 months notice)
v2.0 Beta           : October 2024   (3 months testing)
v2.0 Released       : January 2025
v1.0 Deprecated     : January 2026   (12 months migration)
v1.0 Sunset         : July 2026      (6 months grace)
```

### Deprecation Headers

```http
X-API-Deprecated: true
X-API-Deprecation-Date: 2026-01-01
X-API-Sunset-Date: 2026-07-01
X-API-Migration-Guide: https://docs.example.com/migration/v1-to-v2
```

### Deprecation Warnings

```python
# src/app/api/middleware/deprecation.py
class DeprecationMiddleware:
    """Add deprecation warnings to responses."""

    DEPRECATED_ENDPOINTS = {
        "/api/v1/users/list": {
            "deprecated_date": "2026-01-01",
            "sunset_date": "2026-07-01",
            "alternative": "/api/v2/users",
            "migration_guide": "https://docs.example.com/migration/users-endpoint"
        }
    }

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)

        # Check if endpoint is deprecated
        path = str(request.url.path)
        if path in self.DEPRECATED_ENDPOINTS:
            deprecation = self.DEPRECATED_ENDPOINTS[path]

            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Deprecation-Date"] = deprecation["deprecated_date"]
            response.headers["X-API-Sunset-Date"] = deprecation["sunset_date"]
            response.headers["X-API-Alternative"] = deprecation["alternative"]
            response.headers["X-API-Migration-Guide"] = deprecation["migration_guide"]

            # Log deprecation usage
            logger.warning(
                "Deprecated endpoint used",
                endpoint=path,
                client_id=request.headers.get("X-Client-ID"),
                user_agent=request.headers.get("User-Agent")
            )

        return response
```

## Client Migration Guide

### SDK Version Compatibility

```typescript
// TypeScript SDK
const client = new FullStackClient({
  baseURL: 'https://api.example.com',
  apiVersion: 'v2'  // Specify version
});

// Automatic version negotiation
const client = new FullStackClient({
  baseURL: 'https://api.example.com',
  preferredVersions: ['v2', 'v1'],  // Fallback order
  minVersion: 'v1'  // Minimum acceptable version
});
```

### Migration Checklist

- [ ] Review breaking changes documentation
- [ ] Update SDK to latest version
- [ ] Test against new API version in staging
- [ ] Update error handling for new error codes
- [ ] Modify code for changed endpoints
- [ ] Update data models for new fields
- [ ] Plan rollback strategy
- [ ] Monitor deprecation warnings
- [ ] Complete migration before sunset date

### Version Detection

```javascript
// Check API version
const version = await client.getApiVersion();
console.log(`API Version: ${version.current}`);
console.log(`Supported: ${version.supported.join(', ')}`);

// Handle version-specific logic
if (version.current >= '2.0') {
  // Use v2 features
  const stats = await client.getUsersWithStats();
} else {
  // Fallback to v1
  const users = await client.getUsers();
}
```

## Version Support Matrix

| Version | Status | Released | Deprecated | Sunset | Support Level |
|---------|--------|----------|------------|--------|---------------|
| v1.0 | Active | 2024-01 | - | - | Full Support |
| v1.1 | Active | 2024-04 | - | - | Full Support |
| v1.2 | Active | 2024-07 | - | - | Full Support |
| v2.0 | Beta | 2025-01 | - | - | Beta Support |

### Support Levels

- **Full Support**: All bugs fixed, security patches, performance improvements
- **Security Support**: Security patches only
- **Beta Support**: Preview features, may change
- **Deprecated**: Warning headers, migration guide available
- **Sunset**: No support, may be removed

## Implementation Roadmap

### Phase 1: Foundation (Current)
- [x] URL path versioning structure
- [x] Version configuration in settings
- [x] Basic v1 implementation

### Phase 2: Enhanced Versioning
- [ ] Version detection middleware
- [ ] Header-based minor versioning
- [ ] Conditional response fields
- [ ] Deprecation warning system

### Phase 3: Multi-Version Support
- [ ] Parallel version deployment
- [ ] Version-specific documentation
- [ ] Automated migration tools
- [ ] Version usage analytics

### Phase 4: Advanced Features
- [ ] API version negotiation
- [ ] Feature flags per version
- [ ] Gradual rollout capabilities
- [ ] A/B testing infrastructure

## Best Practices

### For API Developers

1. **Plan for Change**: Design with versioning in mind
2. **Document Everything**: Keep changelog updated
3. **Test Compatibility**: Automated tests for each version
4. **Monitor Usage**: Track version adoption
5. **Communicate Early**: Announce changes well in advance

### For API Consumers

1. **Specify Version**: Always specify desired API version
2. **Handle Deprecation**: Monitor deprecation headers
3. **Test Upgrades**: Test new versions before migration
4. **Stay Updated**: Keep SDKs current
5. **Plan Migration**: Don't wait until sunset date

## Monitoring and Analytics

### Metrics to Track

```python
# Version usage
GET /api/metrics/version-usage
{
  "v1.0": { "requests": 45000, "percentage": 60 },
  "v1.1": { "requests": 25000, "percentage": 33 },
  "v1.2": { "requests": 5000, "percentage": 7 }
}

# Deprecated endpoint usage
GET /api/metrics/deprecated-usage
{
  "/api/v1/old-endpoint": {
    "daily_requests": 1200,
    "unique_clients": 15,
    "sunset_date": "2026-07-01"
  }
}
```

### Alerting Rules

1. **High deprecated endpoint usage** (>1000 requests/day)
2. **Client using soon-to-sunset version** (<30 days)
3. **Version adoption below target** (<50% after 6 months)
4. **Breaking change impact** (>10% error rate increase)

## Communication Strategy

### Channels
- API Changelog: `/changelog`
- Email notifications to registered developers
- Dashboard announcements
- SDK release notes
- Blog posts for major changes

### Timeline
- **T-6 months**: Announce new version
- **T-3 months**: Beta release
- **T-1 month**: Final migration reminder
- **T-0**: New version live
- **T+12 months**: Deprecation begins
- **T+18 months**: Sunset date

## Conclusion

This versioning strategy ensures:
- **Predictability**: Clear timelines and processes
- **Compatibility**: Smooth migration paths
- **Innovation**: Ability to evolve the API
- **Stability**: Long support windows

By following this strategy, we maintain a balance between API stability and the ability to innovate and improve our services.
