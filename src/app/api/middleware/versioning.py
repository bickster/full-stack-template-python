"""API versioning middleware."""

from typing import Any, Dict

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import logger


class VersioningMiddleware(BaseHTTPMiddleware):
    """Handle API versioning through headers and paths."""

    SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2"]
    DEFAULT_VERSION = "1.0"
    DEPRECATED_ENDPOINTS: Dict[str, Dict[str, str]] = {
        # Example deprecated endpoints
        # "/api/v1/users/list": {
        #     "deprecated_date": "2026-01-01",
        #     "sunset_date": "2026-07-01",
        #     "alternative": "/api/v1/users",
        #     "migration_guide": (
        #         "https://docs.example.com/migration/users-endpoint"
        #     )
        # }
    }

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request and add versioning information."""
        # Extract version from header
        header_version = request.headers.get("X-API-Version")

        # Extract version from path
        path_parts = request.url.path.split("/")
        path_version = None
        if len(path_parts) > 2 and path_parts[2].startswith("v"):
            path_version = path_parts[2][1:]  # Remove 'v' prefix

        # Determine final version
        if header_version:
            version = header_version
        elif path_version:
            # Default to .0 for major version in path
            version = f"{path_version}.0"
        else:
            version = self.DEFAULT_VERSION

        # Validate version
        if version not in self.SUPPORTED_VERSIONS:
            logger.warning(
                "unsupported_api_version",
                version=version,
                path=request.url.path,
                client_ip=request.client.host if request.client else None,
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported API version: {version}. "
                    f"Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}"
                ),
            )

        # Store version in request state
        request.state.api_version = version

        # Log API version usage
        logger.info(
            "api_version_used",
            version=version,
            path=request.url.path,
            method=request.method,
        )

        # Process request
        response: Response = await call_next(request)

        # Add version headers to response
        response.headers["X-API-Version"] = version

        # Check for deprecation
        path = str(request.url.path)
        if path in self.DEPRECATED_ENDPOINTS:
            deprecation = self.DEPRECATED_ENDPOINTS[path]

            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Deprecation-Date"] = deprecation[
                "deprecated_date"
            ]
            response.headers["X-API-Sunset-Date"] = deprecation["sunset_date"]
            response.headers["X-API-Alternative"] = deprecation["alternative"]
            response.headers["X-API-Migration-Guide"] = deprecation[
                "migration_guide"
            ]

            # Log deprecation usage
            logger.warning(
                "deprecated_endpoint_used",
                endpoint=path,
                version=version,
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
                deprecation_date=deprecation["deprecated_date"],
                sunset_date=deprecation["sunset_date"],
            )
        else:
            response.headers["X-API-Deprecated"] = "false"

        return response


def get_api_version(request: Request) -> str:
    """Get API version from request state."""
    return getattr(
        request.state, "api_version", VersioningMiddleware.DEFAULT_VERSION
    )


def version_greater_equal(version: str, target: str) -> bool:
    """Check if version is greater than or equal to target."""
    version_parts = [int(x) for x in version.split(".")]
    target_parts = [int(x) for x in target.split(".")]

    # Pad with zeros if needed
    while len(version_parts) < len(target_parts):
        version_parts.append(0)
    while len(target_parts) < len(version_parts):
        target_parts.append(0)

    return version_parts >= target_parts
