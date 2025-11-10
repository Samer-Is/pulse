"""
AI Gateway - Multi-model routing, metering, and rate limiting.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .core.config import get_settings
from .core.logging import setup_logging, get_logger, set_trace_id, get_trace_id

# Import routes (will be created)
# from .routes import chat, images, video

settings = get_settings()
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Pulse AI Studio Gateway",
    description="AI Gateway for multi-model routing, metering, and rate limiting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gateway is internal, backend handles auth
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_trace_id_middleware(request: Request, call_next):
    """Middleware to add trace_id and log requests."""
    trace_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Trace-ID")
        or set_trace_id()
    )
    
    set_trace_id(trace_id)
    
    start_time = time.time()
    logger.info(
        "Gateway request started",
        method=request.method,
        url=str(request.url),
    )
    
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "Gateway request completed",
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Pulse AI Studio Gateway",
        "docs": "/docs",
        "version": "1.0.0",
    }


# Include routers
from .routes import chat

app.include_router(chat.router, prefix="/v1/chat", tags=["Chat"])
# app.include_router(images.router, prefix="/v1/images", tags=["Images"])
# app.include_router(video.router, prefix="/v1/video", tags=["Video"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,
    )
