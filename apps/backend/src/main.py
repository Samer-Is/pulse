"""
Main FastAPI application for Pulse AI Studio Backend.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from .core.config import get_settings
from .core.logging import setup_logging, get_logger, set_trace_id, get_trace_id
from .core.db import init_db

# Import routers (will be created)
# from .api.v1 import auth, plans, payments, usage, files, cv, slides

settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Pulse AI Studio Backend API", env=settings.ENV)
    
    # Initialize database (use Alembic in production)
    if settings.ENV == "development":
        init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pulse AI Studio Backend API")


app = FastAPI(
    title="Pulse AI Studio Backend API",
    description="Backend API for Pulse AI Studio - Arabic-first AI workspace",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_trace_id_middleware(request: Request, call_next):
    """Middleware to add trace_id to every request."""
    # Extract or generate trace ID
    trace_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Trace-ID")
        or set_trace_id()
    )
    
    set_trace_id(trace_id)
    
    # Log request
    start_time = time.time()
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else None,
    )
    
    # Process request
    response = await call_next(request)
    
    # Add trace ID to response headers
    response.headers["X-Trace-ID"] = trace_id
    
    # Log response
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors."""
    logger.warning("Validation error", errors=exc.errors())
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Request validation failed",
                "details": exc.errors(),
            },
            "meta": {
                "trace_id": get_trace_id(),
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error("Unhandled exception", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None,
            },
            "meta": {
                "trace_id": get_trace_id(),
            },
        },
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "backend",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Pulse AI Studio Backend API",
        "docs": "/docs",
        "version": "1.0.0",
    }


# Include API routers
from .api.v1 import auth, plans, payments, usage

app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(plans.router, prefix="/v1/plans", tags=["Plans"])
app.include_router(payments.router, prefix="/v1/payments", tags=["Payments"])
app.include_router(usage.router, prefix="/v1/usage", tags=["Usage"])
# app.include_router(files.router, prefix="/v1/files", tags=["Files"])
# app.include_router(cv.router, prefix="/v1/cv", tags=["CV Maker"])
# app.include_router(slides.router, prefix="/v1/slides", tags=["Slides"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging
    )
