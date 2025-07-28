"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.middleware import VersioningMiddleware
from app.api.openapi import custom_openapi
from app.api.routes import auth, users
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import LoggingMiddleware, logger, setup_logging
from app.core.monitoring import MetricsMiddleware, get_metrics
from app.db.init_db import check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    logger.info("application_startup", app_name=settings.APP_NAME)

    # Check database connection
    if await check_db_connection():
        logger.info("database_connected")
    else:
        logger.error("database_connection_failed")

    yield

    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/api/docs",  # Always available but protected in production
    redoc_url="/api/redoc",  # Always available but protected in production
    openapi_url="/api/openapi.json",
)

# Add middleware
app.add_middleware(VersioningMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure based on your needs
)


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next: Any) -> Response:
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Remove server header
    if "Server" in response.headers:
        del response.headers["Server"]

    return cast(Response, response)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions."""
    logger.error(
        "app_exception",
        error_code=exc.code,
        error_message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "validation_error",
        errors=errors,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "code": "VALIDATION_ERROR",
            "details": {"errors": errors},
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
        },
    )


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)


# Override the openapi method
def custom_openapi_schema() -> Dict[str, Any]:
    """Override OpenAPI schema generation."""
    return cast(Dict[str, Any], custom_openapi(app))


app.openapi = custom_openapi_schema  # type: ignore[method-assign]


# Health check
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    db_ok = await check_db_connection()

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "version": "1.0.0",
    }


# Metrics endpoint
@app.get("/metrics", include_in_schema=False)
async def metrics() -> PlainTextResponse:
    """Prometheus metrics endpoint."""
    metrics_data = await get_metrics()
    return PlainTextResponse(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
    )


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/api/docs",
        "health": "/health",
        "version": "/api/version",
    }


# Version endpoint
@app.get("/api/version")
async def get_version_info() -> dict[str, Any]:
    """Get API version information."""
    from app.api.middleware.versioning import VersioningMiddleware

    return {
        "current": VersioningMiddleware.DEFAULT_VERSION,
        "supported": VersioningMiddleware.SUPPORTED_VERSIONS,
        "deprecated": list(VersioningMiddleware.DEPRECATED_ENDPOINTS.keys()),
        "api_version_header": "X-API-Version",
        "documentation": "/api/docs",
    }
