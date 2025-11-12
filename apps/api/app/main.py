"""
Pulse AI Studio - FastAPI Backend
Main application entry point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .database import init_db, close_db
from .routers import api_router
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    from .utils.secrets import load_secrets_to_env
    
    # Load secrets from AWS Secrets Manager
    load_secrets_to_env()
    
    # Initialize database
    await init_db()
    
    yield
    
    # Shutdown
    await close_db()


app = FastAPI(
    title="Pulse AI Studio API",
    description="Multi-feature AI platform backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting Middleware
app.add_middleware(
    RateLimitMiddleware,
    calls_limit=100,  # 100 requests
    period=60,  # per minute
)

# CORS Configuration
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Trusted Host Middleware (for production)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(","),
    )

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return JSONResponse(
        content={
            "service": "Pulse AI Studio API",
            "version": "0.1.0",
            "status": "healthy",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

