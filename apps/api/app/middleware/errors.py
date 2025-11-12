"""Global error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..utils.logging import logger, log_error
from ..utils.quota import QuotaError


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSON error response
    """
    log_error(
        logger,
        exc,
        context={
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
        
    Returns:
        JSON error response
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),  # Skip 'body'
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        "Validation error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "errors": errors,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Invalid request data",
                "details": errors,
            }
        },
    )


async def quota_exception_handler(request: Request, exc: QuotaError):
    """
    Handle quota exceeded errors.
    
    Args:
        request: FastAPI request
        exc: Quota error
        
    Returns:
        JSON error response
    """
    logger.warning(
        "Quota exceeded",
        extra={
            "method": request.method,
            "path": request.url.path,
            "limit": exc.limit,
            "used": exc.used,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "type": "quota_exceeded",
                "message": exc.message,
                "limit": exc.limit,
                "used": exc.used,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    log_error(
        logger,
        exc,
        context={
            "method": request.method,
            "path": request.url.path,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )

