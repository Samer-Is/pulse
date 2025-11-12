"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..schemas.user import UserResponse, UserUpdate
from ..schemas.subscription import SubscriptionResponse
from ..auth.dependencies import require_auth

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_auth),
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update current authenticated user.
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Update user fields
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.picture is not None:
        current_user.picture = user_update.picture
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current authenticated user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "User account deleted successfully"}


@router.get("/me/subscription", response_model=SubscriptionResponse)
async def get_current_user_subscription(
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    """
    Get current user's subscription.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Subscription information
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    return SubscriptionResponse.model_validate(subscription)

