"""Security headers middleware."""

import time
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logging import logger, log_request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses and log requests.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Add security headers to response and log request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers
        """
        start_time = time.time()
        
        response: Response = await call_next(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log request
        log_request(
            logger,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # HSTS - Force HTTPS in production
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and sanitize incoming requests.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Validate request before processing.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            Response
        """
        # Check request size (prevent large payloads)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(
                "Request too large",
                extra={"content_length": content_length, "path": request.url.path},
            )
            return Response(
                content='{"detail":"Request too large"}',
                status_code=413,
                media_type="application/json",
            )
        
        # Check user agent (basic bot detection - log only)
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["curl", "wget", "python-requests", "scanner", "bot"]
        if any(agent in user_agent for agent in suspicious_agents):
            logger.info(
                "Suspicious user agent detected",
                extra={"user_agent": user_agent, "path": request.url.path},
            )
        
        response = await call_next(request)
        return response

