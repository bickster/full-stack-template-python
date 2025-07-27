"""Structured logging configuration."""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(
    logger: Any, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add application context to log entries."""
    event_dict["app_name"] = settings.APP_NAME
    event_dict["environment"] = (
        "development" if settings.DEBUG else "production"
    )
    return event_dict


def drop_color_message_key(
    logger: Any, method_name: str, event_dict: EventDict
) -> EventDict:
    """Remove color message key for production."""
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )

    # Configure structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.DEBUG:
        # Development processors
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )
    else:
        # Production processors
        processors.extend(
            [
                drop_color_message_key,
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Initialize logger
logger = structlog.get_logger()


class LoggingMiddleware:
    """Middleware for request/response logging."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Log requests and responses."""
        if scope["type"] == "http":
            # Log request
            logger.info(
                "http_request",
                method=scope["method"],
                path=scope["path"],
                query_string=scope["query_string"].decode(),
            )

        await self.app(scope, receive, send)


def log_error(
    error: Exception, context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with context."""
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True,
    )


def log_audit(
    action: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an audit event."""
    logger.info(
        "audit_log",
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
