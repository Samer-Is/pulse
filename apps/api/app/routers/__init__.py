"""API routers."""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .jobs import router as jobs_router
from .chat import router as chat_router
from .health import router as health_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]

