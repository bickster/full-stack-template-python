"""Rate limiting implementation."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.db.models.login_attempt import LoginAttempt


class RateLimiter:
    """Rate limiter for API endpoints."""

    def __init__(
        self,
        max_requests: int,
        window_minutes: int,
        identifier_field: str = "ip_address",
    ):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.identifier_field = identifier_field

    async def check_rate_limit(
        self,
        db: AsyncSession,
        identifier: str,
        raise_on_limit: bool = True,
    ) -> tuple[bool, int]:
        """Check if rate limit is exceeded.
        
        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        # This is a simple in-memory implementation
        # In production, use Redis for distributed rate limiting
        
        # For now, we'll just return allowed
        # TODO: Implement proper rate limiting with Redis
        return True, self.max_requests


class LoginRateLimiter:
    """Rate limiter specifically for login attempts."""

    def __init__(
        self,
        max_attempts: int = settings.LOGIN_RATE_LIMIT_PER_MINUTE * 3,
        window_minutes: int = 15,
    ):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes

    async def check_login_rate_limit(
        self,
        db: AsyncSession,
        email: str,
        ip_address: str,
    ) -> tuple[bool, int, Optional[datetime]]:
        """Check if login rate limit is exceeded.
        
        Returns:
            tuple: (is_allowed, remaining_attempts, retry_after)
        """
        # Calculate the time window
        window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        
        # Count recent failed login attempts
        result = await db.execute(
            select(func.count(LoginAttempt.id))
            .where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.attempted_at >= window_start,
                    LoginAttempt.success == False,
                )
            )
        )
        
        failed_attempts = result.scalar() or 0
        
        if failed_attempts >= self.max_attempts:
            # Get the oldest attempt in the window to calculate retry time
            oldest_result = await db.execute(
                select(LoginAttempt.attempted_at)
                .where(
                    and_(
                        LoginAttempt.email == email,
                        LoginAttempt.ip_address == ip_address,
                        LoginAttempt.attempted_at >= window_start,
                        LoginAttempt.success == False,
                    )
                )
                .order_by(LoginAttempt.attempted_at)
                .limit(1)
            )
            
            oldest_attempt = oldest_result.scalar()
            if oldest_attempt:
                retry_after = oldest_attempt + timedelta(minutes=self.window_minutes)
                return False, 0, retry_after
            
            return False, 0, None
        
        remaining = self.max_attempts - failed_attempts
        return True, remaining, None

    async def record_login_attempt(
        self,
        db: AsyncSession,
        email: str,
        ip_address: str,
        success: bool,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Record a login attempt."""
        attempt = LoginAttempt(
            email=email,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )
        
        db.add(attempt)
        await db.commit()


# Global instances
login_rate_limiter = LoginRateLimiter()
api_rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window_minutes=1,
)