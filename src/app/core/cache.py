"""Cache management."""

from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from app.core.config import settings
from app.core.logging import logger


class CacheEntry:
    """Cache entry with TTL support."""

    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.ttl = ttl
        self.created_at = self._now()

    def _now(self) -> float:
        """Get current timestamp."""
        import time

        return time.time()

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return self._now() - self.created_at > self.ttl


class InMemoryCache:
    """Simple in-memory cache implementation."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._storage: Dict[str, CacheEntry] = {}
        self._access_order: list[str] = []

    def _evict_oldest(self) -> None:
        """Evict oldest entry when cache is full."""
        if self._access_order:
            oldest_key = self._access_order.pop(0)
            self._storage.pop(oldest_key, None)

    def _update_access_order(self, key: str) -> None:
        """Update access order for LRU."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._storage.get(key)

        if entry is None:
            return None

        if entry.is_expired():
            self.delete(key)
            return None

        self._update_access_order(key)
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if len(self._storage) >= self.max_size and key not in self._storage:
            self._evict_oldest()

        self._storage[key] = CacheEntry(value, ttl)
        self._update_access_order(key)

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._storage:
            del self._storage[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._storage.clear()
        self._access_order.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._storage)


# Global cache instance
cache = InMemoryCache()


def cached(
    ttl: Union[int, timedelta] = settings.CACHE_TTL,
    key_prefix: str = "",
    key_func: Optional[Callable[..., str]] = None,
) -> Callable[..., Any]:
    """Decorator for caching function results."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key generation
                key_parts = [key_prefix, func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(
                        f"{k}:{v}" for k, v in sorted(kwargs.items())
                    )
                cache_key = ":".join(key_parts)

            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug("cache_hit", key=cache_key)
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            ttl_seconds = (
                ttl.total_seconds() if isinstance(ttl, timedelta) else ttl
            )
            cache.set(cache_key, result, int(ttl_seconds))
            logger.debug("cache_set", key=cache_key, ttl=ttl_seconds)

            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key generation
                key_parts = [key_prefix, func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(
                        f"{k}:{v}" for k, v in sorted(kwargs.items())
                    )
                cache_key = ":".join(key_parts)

            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug("cache_hit", key=cache_key)
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            ttl_seconds = (
                ttl.total_seconds() if isinstance(ttl, timedelta) else ttl
            )
            cache.set(cache_key, result, int(ttl_seconds))
            logger.debug("cache_set", key=cache_key, ttl=ttl_seconds)

            return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Specialized cache decorators
def cache_user(ttl: int = 300) -> Callable[..., Any]:
    """Cache decorator for user-related operations."""
    return cached(ttl=ttl, key_prefix="user")


def cache_auth(ttl: int = 60) -> Callable[..., Any]:
    """Cache decorator for auth-related operations."""
    return cached(ttl=ttl, key_prefix="auth")
