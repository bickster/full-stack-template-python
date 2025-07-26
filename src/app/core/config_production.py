"""Production-specific configuration overrides."""

import os
from typing import List

from app.core.config import Settings


class ProductionSettings(Settings):
    """Production configuration settings."""
    
    # Override defaults for production
    DEBUG: bool = False
    TESTING: bool = False
    
    # Stricter CORS in production
    @property
    def BACKEND_CORS_ORIGINS_LIST(self) -> List[str]:
        """Get CORS origins from environment."""
        origins = os.getenv("BACKEND_CORS_ORIGINS", "")
        if origins:
            return [origin.strip() for origin in origins.split(",")]
        return []
    
    # Force HTTPS in production
    @property
    def FRONTEND_URL(self) -> str:
        """Ensure HTTPS for frontend URL."""
        url = super().FRONTEND_URL
        if url.startswith("http://") and not url.startswith("http://localhost"):
            return url.replace("http://", "https://")
        return url
    
    # Production logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"
    
    # Production database pool settings
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Production rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 3
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    SENTRY_ENABLED: bool = True
    
    class Config:
        """Production config."""
        env_file = ".env.production"
        case_sensitive = True


# Use production settings if in production
if os.getenv("ENVIRONMENT", "development") == "production":
    settings = ProductionSettings()
else:
    from app.core.config import settings