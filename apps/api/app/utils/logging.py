"""Structured logging utilities."""

import os
import sys
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = None) -> logging.Logger:
    """
    Setup structured JSON logging.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    logger = logging.getLogger("pulse")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        timestamp=True,
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float):
    """
    Log HTTP request.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration: Request duration in seconds
    """
    logger.info(
        "HTTP request",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )


def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log error with context.
    
    Args:
        logger: Logger instance
        error: Exception
        context: Additional context
    """
    extra = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        extra.update(context)
    
    logger.error("Error occurred", extra=extra, exc_info=True)


def log_usage_event(
    logger: logging.Logger,
    user_id: str,
    event_type: str,
    tokens: int = 0,
    metadata: dict = None,
):
    """
    Log usage event.
    
    Args:
        logger: Logger instance
        user_id: User ID
        event_type: Event type
        tokens: Tokens used
        metadata: Additional metadata
    """
    extra = {
        "user_id": user_id,
        "event_type": event_type,
        "tokens": tokens,
    }
    
    if metadata:
        extra.update(metadata)
    
    logger.info("Usage event", extra=extra)


# Global logger instance
logger = setup_logging()

