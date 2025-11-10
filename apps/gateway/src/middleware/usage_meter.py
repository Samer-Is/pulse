"""
Usage metering middleware.

Logs AI usage to database for quota enforcement.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import httpx

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class UsageMeteringMiddleware(BaseHTTPMiddleware):
    """
    Usage metering middleware.
    
    Tracks:
    - Token usage (from AI responses)
    - Image generation count
    - Video generation count
    
    Logs to backend API for quota enforcement.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Skip metering for health/non-AI endpoints
        if request.url.path in ["/health", "/v1/chat/models"]:
            return response
        
        # Extract usage from response
        try:
            # Get user ID from request
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                return response
            
            # Determine resource type and amount
            resource_type = None
            amount = 0
            
            if "/chat/" in request.url.path:
                # TODO: Extract token usage from response body
                # For now, use a stub
                resource_type = "tokens"
                amount = 500  # Stub value
            elif "/images/" in request.url.path:
                resource_type = "images"
                amount = 1
            elif "/video/" in request.url.path:
                resource_type = "videos"
                amount = 1
            
            if resource_type and amount > 0:
                # Log usage to backend asynchronously
                await self.log_usage(user_id, resource_type, amount)
            
        except Exception as e:
            logger.error(f"Usage metering error: {str(e)}")
            # Don't fail the request if metering fails
        
        # Add timing header
        duration = time.time() - start_time
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
    
    async def log_usage(self, user_id: str, resource_type: str, amount: int):
        """Log usage to backend API."""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.BACKEND_URL}/v1/usage/log",
                    json={
                        "resource_type": resource_type,
                        "amount": amount,
                        "metadata": {}
                    },
                    headers={"X-User-ID": user_id},
                    timeout=2.0
                )
            logger.info(f"Usage logged: user={user_id}, type={resource_type}, amount={amount}")
        except Exception as e:
            logger.error(f"Failed to log usage: {str(e)}")

