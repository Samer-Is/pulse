"""
FastAPI dependencies for authentication, authorization, etc.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session

from .db import get_db
from .security import decode_access_token
from .logging import get_logger, set_trace_id
from ..models.user import User

logger = get_logger(__name__)


async def get_current_user(
    request: Request,
    session: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT cookie.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    # Set trace ID for logging
    trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID")
    set_trace_id(trace_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode JWT token
    payload = decode_access_token(session)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_user_optional(
    request: Request,
    session: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Similar to get_current_user but returns None instead of raising exception.
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    try:
        return await get_current_user(request, session, db)
    except HTTPException:
        return None


def require_plan(required_plan: str):
    """
    Dependency factory to require specific plan level.
    
    Usage:
        @app.get("/pro-feature")
        async def pro_feature(user: User = Depends(require_plan("Pro"))):
            return {"message": "Pro feature"}
    """
    async def check_plan(user: User = Depends(get_current_user)) -> User:
        # Check if user has active subscription
        if not hasattr(user, "subscription") or not user.subscription:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Active subscription required",
            )
        
        # Check plan level (Starter < Pro < Creator)
        plan_hierarchy = {"Starter": 1, "Pro": 2, "Creator": 3}
        user_plan_level = plan_hierarchy.get(user.subscription.plan.name, 0)
        required_plan_level = plan_hierarchy.get(required_plan, 999)
        
        if user_plan_level < required_plan_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"{required_plan} plan or higher required",
                headers={"X-Upgrade-URL": "/app/account/upgrade"},
            )
        
        return user
    
    return check_plan
