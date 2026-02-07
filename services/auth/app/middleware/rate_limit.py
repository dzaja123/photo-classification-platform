"""Rate limiting middleware using Redis."""

from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.cache import increment_rate_limit, get_rate_limit_ttl


def parse_rate_limit(rate_string: str) -> tuple[int, int]:
    """
    Parse rate limit string (e.g., "5/minute", "100/hour").

    Args:
        rate_string: Rate limit in format "count/period"

    Returns:
        Tuple of (max_requests, window_seconds)

    Example:
        >>> parse_rate_limit("5/minute")
        (5, 60)
        >>> parse_rate_limit("100/hour")
        (100, 3600)
    """
    count, period = rate_string.split("/")
    max_requests = int(count)

    period_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}

    window = period_map.get(period.lower(), 60)

    return max_requests, window


def rate_limit(rate: str, key_prefix: str = "rate_limit"):
    """
    Rate limiting decorator for FastAPI endpoints.

    Args:
        rate: Rate limit string (e.g., "5/minute", "100/hour")
        key_prefix: Redis key prefix

    Returns:
        Decorator function

    Usage:
        @router.post("/login")
        @rate_limit("5/minute", key_prefix="login")
        async def login(request: Request, ...):
            ...

    Example:
        # Allow 5 requests per minute per IP
        @rate_limit("5/minute", key_prefix="login")

        # Allow 100 requests per hour per IP
        @rate_limit("100/hour", key_prefix="api")
    """
    max_requests, window = parse_rate_limit(rate)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request: Request = kwargs.get("request") or next(
                (arg for arg in args if isinstance(arg, Request)), None
            )

            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)

            # Get client IP
            client_ip = request.client.host if request.client else "unknown"

            # Check X-Forwarded-For header
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

            # Create rate limit key
            endpoint = request.url.path
            rate_key = f"{key_prefix}:{endpoint}:{client_ip}"

            # Check rate limit
            is_allowed, current_count = await increment_rate_limit(
                rate_key, window, max_requests
            )

            # Add rate limit headers to response
            if hasattr(request.state, "rate_limit_headers"):
                request.state.rate_limit_headers = {}

            ttl = await get_rate_limit_ttl(rate_key)

            # Set response headers (will be added by middleware)
            request.state.rate_limit_limit = max_requests
            request.state.rate_limit_remaining = max(0, max_requests - current_count)
            request.state.rate_limit_reset = ttl if ttl > 0 else window

            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(ttl),
                        "Retry-After": str(ttl),
                    },
                )

            # Call the actual endpoint
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def add_rate_limit_headers(request: Request, call_next):
    """
    Middleware to add rate limit headers to all responses.

    Args:
        request: FastAPI request
        call_next: Next middleware in chain

    Returns:
        Response with rate limit headers
    """
    response = await call_next(request)

    # Add rate limit headers if they were set
    if hasattr(request.state, "rate_limit_limit"):
        response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            request.state.rate_limit_remaining
        )
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)

    return response
