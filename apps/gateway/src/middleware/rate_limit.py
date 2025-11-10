"""
Rate limiting middleware using Redis.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from typing import Callable
import time

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Redis client for rate limiting
redis_client = None


async def get_redis():
    """Get or create Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Limits: 
    - 60 requests per minute per user
    - 1000 requests per hour per user
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get user identifier (from JWT or IP)
        user_id = request.headers.get("X-User-ID", request.client.host)
        
        try:
            redis_conn = await get_redis()
            
            # Check minute limit
            minute_key = f"rate_limit:minute:{user_id}:{int(time.time() / 60)}"
            minute_count = await redis_conn.incr(minute_key)
            await redis_conn.expire(minute_key, 60)
            
            if minute_count > 60:
                logger.warning(f"Rate limit exceeded (minute): user={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded: 60 requests per minute"
                )
            
            # Check hour limit
            hour_key = f"rate_limit:hour:{user_id}:{int(time.time() / 3600)}"
            hour_count = await redis_conn.incr(hour_key)
            await redis_conn.expire(hour_key, 3600)
            
            if hour_count > 1000:
                logger.warning(f"Rate limit exceeded (hour): user={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded: 1000 requests per hour"
                )
            
            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit-Minute"] = "60"
            response.headers["X-RateLimit-Remaining-Minute"] = str(60 - minute_count)
            response.headers["X-RateLimit-Limit-Hour"] = "1000"
            response.headers["X-RateLimit-Remaining-Hour"] = str(1000 - hour_count)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Fail open - allow request if Redis is down
            return await call_next(request)

