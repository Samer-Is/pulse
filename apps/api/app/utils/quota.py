"""Quota checking and enforcement utilities."""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from ..models.user import User
from ..models.subscription import Subscription
from ..models.usage import UsageEvent

# Plan definitions (from shared package)
PLANS = {
    "starter": {
        "name": "Starter",
        "price": 9,
        "limits": {
            "chat_tokens": 100_000,
            "image_creations": 50,
            "video_seconds": 30,
            "cv_exports": 5,
            "slide_exports": 5,
        },
    },
    "plus": {
        "name": "Plus",
        "price": 29,
        "limits": {
            "chat_tokens": 500_000,
            "image_creations": 200,
            "video_seconds": 120,
            "cv_exports": 20,
            "slide_exports": 20,
        },
    },
    "pro": {
        "name": "Pro",
        "price": 99,
        "limits": {
            "chat_tokens": 2_000_000,
            "image_creations": 1000,
            "video_seconds": 600,
            "cv_exports": 100,
            "slide_exports": 100,
        },
    },
}


class QuotaError(Exception):
    """Raised when quota is exceeded."""

    def __init__(self, message: str, limit: int, used: int):
        self.message = message
        self.limit = limit
        self.used = used
        super().__init__(self.message)


async def get_user_subscription(user: User, db: AsyncSession) -> Subscription:
    """
    Get user's active subscription.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        Subscription object
        
    Raises:
        HTTPException: If no subscription found or expired
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found. Please subscribe to a plan.",
        )
    
    # Check if subscription is active and not expired
    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Subscription is {subscription.status}. Please renew your subscription.",
        )
    
    if subscription.period_end < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription has expired. Please renew your subscription.",
        )
    
    return subscription


async def check_chat_quota(
    user: User,
    db: AsyncSession,
    tokens_to_use: int = 0,
) -> Subscription:
    """
    Check if user has remaining chat token quota.
    
    Args:
        user: Current user
        db: Database session
        tokens_to_use: Estimated tokens to use (for pre-check)
        
    Returns:
        User's subscription
        
    Raises:
        QuotaError: If quota exceeded
    """
    subscription = await get_user_subscription(user, db)
    
    # Get plan limits
    plan = PLANS.get(subscription.plan_id)
    if not plan:
        raise ValueError(f"Invalid plan_id: {subscription.plan_id}")
    
    limit = plan["limits"]["chat_tokens"]
    used = subscription.chat_tokens_used
    
    # Check if quota exceeded
    if used + tokens_to_use > limit:
        raise QuotaError(
            f"Chat token quota exceeded. Used: {used}/{limit}",
            limit=limit,
            used=used,
        )
    
    return subscription


async def check_image_quota(user: User, db: AsyncSession, count: int = 1) -> Subscription:
    """
    Check if user has remaining image generation quota.
    
    Args:
        user: Current user
        db: Database session
        count: Number of images to generate
        
    Returns:
        User's subscription
        
    Raises:
        QuotaError: If quota exceeded
    """
    subscription = await get_user_subscription(user, db)
    
    # Get plan limits
    plan = PLANS.get(subscription.plan_id)
    if not plan:
        raise ValueError(f"Invalid plan_id: {subscription.plan_id}")
    
    limit = plan["limits"]["image_creations"]
    used = subscription.image_creations_used
    
    # Check if quota exceeded
    if used + count > limit:
        raise QuotaError(
            f"Image generation quota exceeded. Used: {used}/{limit}",
            limit=limit,
            used=used,
        )
    
    return subscription


async def check_video_quota(user: User, db: AsyncSession, seconds: int = 0) -> Subscription:
    """
    Check if user has remaining video generation quota.
    
    Args:
        user: Current user
        db: Database session
        seconds: Estimated video duration in seconds
        
    Returns:
        User's subscription
        
    Raises:
        QuotaError: If quota exceeded
    """
    subscription = await get_user_subscription(user, db)
    
    # Get plan limits
    plan = PLANS.get(subscription.plan_id)
    if not plan:
        raise ValueError(f"Invalid plan_id: {subscription.plan_id}")
    
    limit = plan["limits"]["video_seconds"]
    used = subscription.video_seconds_used
    
    # Check if quota exceeded
    if used + seconds > limit:
        raise QuotaError(
            f"Video generation quota exceeded. Used: {used}/{limit}",
            limit=limit,
            used=used,
        )
    
    return subscription


async def check_cv_quota(user: User, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining CV export quota.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        User's subscription
        
    Raises:
        QuotaError: If quota exceeded
    """
    subscription = await get_user_subscription(user, db)
    
    # Get plan limits
    plan = PLANS.get(subscription.plan_id)
    if not plan:
        raise ValueError(f"Invalid plan_id: {subscription.plan_id}")
    
    limit = plan["limits"]["cv_exports"]
    used = subscription.cvs_generated
    
    # Check if quota exceeded
    if used >= limit:
        raise QuotaError(
            f"CV export quota exceeded. Used: {used}/{limit}",
            limit=limit,
            used=used,
        )
    
    return subscription


async def check_slide_quota(user: User, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining slide export quota.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        User's subscription
        
    Raises:
        QuotaError: If quota exceeded
    """
    subscription = await get_user_subscription(user, db)
    
    # Get plan limits
    plan = PLANS.get(subscription.plan_id)
    if not plan:
        raise ValueError(f"Invalid plan_id: {subscription.plan_id}")
    
    limit = plan["limits"]["slide_exports"]
    used = subscription.slides_generated
    
    # Check if quota exceeded
    if used >= limit:
        raise QuotaError(
            f"Slide export quota exceeded. Used: {used}/{limit}",
            limit=limit,
            used=used,
        )
    
    return subscription


async def increment_chat_usage(
    user_id: str,
    tokens: int,
    db: AsyncSession,
) -> None:
    """
    Increment chat token usage.
    
    Args:
        user_id: User ID
        tokens: Tokens used
        db: Database session
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.chat_tokens_used += tokens
        await db.commit()


async def increment_image_usage(user_id: str, count: int, db: AsyncSession) -> None:
    """
    Increment image generation usage.
    
    Args:
        user_id: User ID
        count: Number of images generated
        db: Database session
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.image_creations_used += count
        await db.commit()


async def increment_video_usage(user_id: str, seconds: int, db: AsyncSession) -> None:
    """
    Increment video generation usage.
    
    Args:
        user_id: User ID
        seconds: Video duration in seconds
        db: Database session
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.video_seconds_used += seconds
        await db.commit()


async def increment_cv_usage(user_id: str, db: AsyncSession) -> None:
    """
    Increment CV export usage.
    
    Args:
        user_id: User ID
        db: Database session
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.cvs_generated += 1
        await db.commit()


async def increment_slide_usage(user_id: str, db: AsyncSession) -> None:
    """
    Increment slide export usage.
    
    Args:
        user_id: User ID
        db: Database session
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.slides_generated += 1
        await db.commit()


async def get_usage_summary(user_id: str, db: AsyncSession) -> dict:
    """
    Get usage summary for user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Usage summary dict
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return {}
    
    plan = PLANS.get(subscription.plan_id, {})
    limits = plan.get("limits", {})
    
    return {
        "plan_id": subscription.plan_id,
        "status": subscription.status,
        "period_start": subscription.period_start.isoformat(),
        "period_end": subscription.period_end.isoformat(),
        "usage": {
            "chat_tokens": {
                "used": subscription.chat_tokens_used,
                "limit": limits.get("chat_tokens", 0),
                "percentage": (subscription.chat_tokens_used / limits.get("chat_tokens", 1)) * 100,
            },
            "images": {
                "used": subscription.image_creations_used,
                "limit": limits.get("image_creations", 0),
                "percentage": (subscription.image_creations_used / limits.get("image_creations", 1)) * 100,
            },
            "videos": {
                "used": subscription.video_seconds_used,
                "limit": limits.get("video_seconds", 0),
                "percentage": (subscription.video_seconds_used / limits.get("video_seconds", 1)) * 100,
            },
            "cvs": {
                "used": subscription.cvs_generated,
                "limit": limits.get("cv_exports", 0),
                "percentage": (subscription.cvs_generated / limits.get("cv_exports", 1)) * 100,
            },
            "slides": {
                "used": subscription.slides_generated,
                "limit": limits.get("slide_exports", 0),
                "percentage": (subscription.slides_generated / limits.get("slide_exports", 1)) * 100,
            },
        },
    }

