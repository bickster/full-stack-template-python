"""Monitoring and metrics."""

from typing import Any, Optional

from prometheus_client import Counter, Gauge, Histogram, generate_latest

from app.core.config import settings

# Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_users_gauge = Gauge(
    "active_users_total",
    "Number of active users",
)

login_attempts_total = Counter(
    "login_attempts_total",
    "Total login attempts",
    ["result"],  # success or failure
)

token_operations_total = Counter(
    "token_operations_total",
    "Total token operations",
    ["operation", "token_type"],  # create/validate/refresh, access/refresh
)

database_operations_total = Counter(
    "database_operations_total",
    "Total database operations",
    ["operation", "table"],
)

database_operation_duration_seconds = Histogram(
    "database_operation_duration_seconds",
    "Database operation duration in seconds",
    ["operation", "table"],
)

cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "result"],  # get/set/delete, hit/miss
)

rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Total rate limit exceeded events",
    ["endpoint"],
)


class MetricsMiddleware:
    """Middleware for collecting metrics."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Collect metrics for each request."""
        if scope["type"] != "http" or not settings.PROMETHEUS_ENABLED:
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        method = scope["method"]

        # Skip metrics endpoint
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        # Record request
        import time

        start_time = time.time()

        # Capture response status
        status_code = 500

        async def send_wrapper(message: Any) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code,
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=path,
            ).observe(duration)


async def get_metrics() -> str:
    """Get Prometheus metrics."""
    return str(generate_latest())


def record_login_attempt(success: bool) -> None:
    """Record a login attempt."""
    result = "success" if success else "failure"
    login_attempts_total.labels(result=result).inc()


def record_token_operation(operation: str, token_type: str) -> None:
    """Record a token operation."""
    token_operations_total.labels(
        operation=operation,
        token_type=token_type,
    ).inc()


def record_database_operation(
    operation: str,
    table: str,
    duration: Optional[float] = None,
) -> None:
    """Record a database operation."""
    database_operations_total.labels(
        operation=operation,
        table=table,
    ).inc()

    if duration is not None:
        database_operation_duration_seconds.labels(
            operation=operation,
            table=table,
        ).observe(duration)


def record_cache_operation(operation: str, hit: Optional[bool] = None) -> None:
    """Record a cache operation."""
    if operation == "get":
        result = "hit" if hit else "miss"
    else:
        result = "success"

    cache_operations_total.labels(
        operation=operation,
        result=result,
    ).inc()


def record_rate_limit_exceeded(endpoint: str) -> None:
    """Record a rate limit exceeded event."""
    rate_limit_exceeded_total.labels(endpoint=endpoint).inc()


def update_active_users(count: int) -> None:
    """Update active users gauge."""
    active_users_gauge.set(count)
