"""Redis cache utilities for Auth Service."""

from typing import Optional
import redis.asyncio as redis

from app.config import get_settings


settings = get_settings()

# Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None


async def get_redis() -> redis.Redis:
    """
    Get Redis connection from pool.

    Returns:
        Redis client instance

    Usage:
        redis_client = await get_redis()
        await redis_client.set("key", "value")
    """
    global redis_pool

    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            str(settings.redis_url),
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )

    return redis.Redis(connection_pool=redis_pool)


async def close_redis():
    """Close Redis connection pool."""
    global redis_pool

    if redis_pool is not None:
        await redis_pool.disconnect()
        redis_pool = None


async def set_cache(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Set a value in Redis cache.

    Args:
        key: Cache key
        value: Value to store
        ttl: Time to live in seconds (optional)

    Returns:
        True if successful

    Example:
        >>> await set_cache("user:123", "data", ttl=300)
        True
    """
    redis_client = await get_redis()
    if ttl:
        await redis_client.setex(key, ttl, value)
    else:
        await redis_client.set(key, value)
    return True


async def get_cache(key: str) -> Optional[str]:
    """
    Get a value from Redis cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found

    Example:
        >>> value = await get_cache("user:123")
        >>> print(value)
        "data"
    """
    redis_client = await get_redis()
    value = await redis_client.get(key)
    return value


async def delete_cache(key: str) -> bool:
    """
    Delete a key from Redis cache.

    Args:
        key: Cache key to delete

    Returns:
        True if key was deleted, False if key didn't exist

    Example:
        >>> await delete_cache("user:123")
        True
    """
    redis_client = await get_redis()
    result = await redis_client.delete(key)
    return result > 0


async def exists_cache(key: str) -> bool:
    """
    Check if a key exists in Redis cache.

    Args:
        key: Cache key to check

    Returns:
        True if key exists, False otherwise

    Example:
        >>> await exists_cache("user:123")
        True
    """
    redis_client = await get_redis()
    result = await redis_client.exists(key)
    return result > 0


async def blacklist_token(jti: str, ttl: int) -> bool:
    """
    Add a JWT token to the blacklist.

    Args:
        jti: JWT ID (from token payload)
        ttl: Time to live in seconds (should match token expiration)

    Returns:
        True if successful

    Example:
        >>> await blacklist_token("token-jti-123", ttl=900)
        True
    """
    redis_client = await get_redis()
    await redis_client.setex(f"blacklist:{jti}", ttl, "1")
    return True


async def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a JWT token is blacklisted.

    Args:
        jti: JWT ID to check

    Returns:
        True if token is blacklisted, False otherwise

    Example:
        >>> await is_token_blacklisted("token-jti-123")
        False
    """
    redis_client = await get_redis()
    result = await redis_client.exists(f"blacklist:{jti}")
    return result > 0


async def increment_rate_limit(
    key: str, window: int, max_requests: int
) -> tuple[bool, int]:
    """
    Increment rate limit counter.

    Args:
        key: Rate limit key (e.g., "rate_limit:login:192.168.1.1")
        window: Time window in seconds
        max_requests: Maximum requests allowed in window

    Returns:
        Tuple of (is_allowed, current_count)

    Example:
        >>> is_allowed, count = await increment_rate_limit(
        ...     "rate_limit:login:192.168.1.1",
        ...     window=60,
        ...     max_requests=5
        ... )
        >>> if not is_allowed:
        ...     raise HTTPException(429, "Too many requests")
    """
    redis_client = await get_redis()

    # Increment counter
    current = await redis_client.incr(key)

    # Set expiration on first request
    if current == 1:
        await redis_client.expire(key, window)

    # Check if limit exceeded
    is_allowed = current <= max_requests

    return is_allowed, current


async def get_rate_limit_ttl(key: str) -> int:
    """
    Get remaining TTL for rate limit key.

    Args:
        key: Rate limit key

    Returns:
        Remaining seconds until reset, or -1 if key doesn't exist

    Example:
        >>> ttl = await get_rate_limit_ttl("rate_limit:login:192.168.1.1")
        >>> print(f"Reset in {ttl} seconds")
    """
    redis_client = await get_redis()
    ttl = await redis_client.ttl(key)
    return ttl if ttl > 0 else -1


async def reset_rate_limit(key: str) -> bool:
    """
    Reset rate limit counter.

    Args:
        key: Rate limit key to reset

    Returns:
        True if successful

    Example:
        >>> await reset_rate_limit("rate_limit:login:192.168.1.1")
        True
    """
    return await delete_cache(key)
