"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Note: For production, use Redis-based rate limiting for distributed systems.
    """

    def __init__(self, app, calls_limit: int = 100, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            app: FastAPI application
            calls_limit: Maximum number of calls allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls_limit = calls_limit
        self.period = period
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Client identifier (IP address or user ID)
        """
        # Try to get user ID from auth header
        auth_header = request.headers.get("authorization")
        if auth_header:
            return f"user:{auth_header[:20]}"  # Use first 20 chars of token
        
        # Fall back to IP address
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        
        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _is_rate_limited(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Check if client is rate limited.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (is_limited, remaining_calls, reset_time)
        """
        now = time.time()
        cutoff = now - self.period
        
        # Clean up old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[client_id])
        remaining = max(0, self.calls_limit - request_count)
        
        if request_count >= self.calls_limit:
            # Calculate when the oldest request will expire
            reset_time = int(self.requests[client_id][0] + self.period)
            return True, 0, reset_time
        
        # Add current request
        self.requests[client_id].append(now)
        reset_time = int(now + self.period)
        
        return False, remaining, reset_time

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            Response
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/", "/health", "/api/v1/health", "/api/v1/health/db"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        is_limited, remaining, reset_time = self._is_rate_limited(client_id)
        
        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.calls_limit} per {self.period} seconds",
                },
                headers={
                    "X-RateLimit-Limit": str(self.calls_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time())),
                },
            )
        
        # Process request
        response: Response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response

