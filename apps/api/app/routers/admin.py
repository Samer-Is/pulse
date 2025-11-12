"""Admin routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..models.usage import UsageEvent
from ..models.job import Job
from ..auth.dependencies import require_admin
from ..schemas.admin import (
    UserListResponse,
    SubscriptionListResponse,
    AnalyticsResponse,
    UserUpdateRequest,
    SubscriptionUpdateRequest,
)
from ..utils.quota import get_usage_summary

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users (admin only).
    
    Args:
        page: Page number
        per_page: Results per page
        search: Search query (email or name)
        admin: Admin user
        db: Database session
        
    Returns:
        List of users
    """
    query = select(User)
    
    # Apply search filter
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user details (admin only).
    
    Args:
        user_id: User ID
        admin: Admin user
        db: Database session
        
    Returns:
        User details with subscription and usage
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get subscription
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    subscription = result.scalar_one_or_none()
    
    # Get usage summary
    usage = await get_usage_summary(user_id, db)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "stripe_customer_id": user.stripe_customer_id,
        "created_at": user.created_at.isoformat(),
        "subscription": {
            "plan_id": subscription.plan_id,
            "status": subscription.status,
            "period_start": subscription.period_start.isoformat(),
            "period_end": subscription.period_end.isoformat(),
        } if subscription else None,
        "usage": usage,
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update: UserUpdateRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user (admin only).
    
    Args:
        user_id: User ID
        update: Update data
        admin: Admin user
        db: Database session
        
    Returns:
        Updated user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Apply updates
    if update.is_active is not None:
        user.is_active = update.is_active
    if update.is_admin is not None:
        user.is_admin = update.is_admin
    
    await db.commit()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user (admin only).
    
    Args:
        user_id: User ID
        admin: Admin user
        db: Database session
        
    Returns:
        Success message
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/subscriptions", response_model=SubscriptionListResponse)
async def list_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    plan_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all subscriptions (admin only).
    
    Args:
        page: Page number
        per_page: Results per page
        status_filter: Filter by status
        plan_filter: Filter by plan
        admin: Admin user
        db: Database session
        
    Returns:
        List of subscriptions
    """
    query = select(Subscription)
    
    # Apply filters
    filters = []
    if status_filter:
        filters.append(Subscription.status == status_filter)
    if plan_filter:
        filters.append(Subscription.plan_id == plan_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return SubscriptionListResponse(
        subscriptions=[
            {
                "id": sub.id,
                "user_id": sub.user_id,
                "plan_id": sub.plan_id,
                "status": sub.status,
                "period_start": sub.period_start.isoformat(),
                "period_end": sub.period_end.isoformat(),
                "created_at": sub.created_at.isoformat(),
            }
            for sub in subscriptions
        ],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    update: SubscriptionUpdateRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update subscription (admin only).
    
    Args:
        subscription_id: Subscription ID
        update: Update data
        admin: Admin user
        db: Database session
        
    Returns:
        Updated subscription
    """
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    # Apply updates
    if update.plan_id is not None:
        subscription.plan_id = update.plan_id
    if update.status is not None:
        subscription.status = update.status
    if update.period_end is not None:
        subscription.period_end = update.period_end
    
    await db.commit()
    
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "status": subscription.status,
        "period_end": subscription.period_end.isoformat(),
    }


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get platform analytics (admin only).
    
    Args:
        admin: Admin user
        db: Database session
        
    Returns:
        Analytics data
    """
    # Total users
    result = await db.execute(select(func.count()).select_from(User))
    total_users = result.scalar()
    
    # Active subscriptions
    result = await db.execute(
        select(func.count()).select_from(Subscription).where(Subscription.status == "active")
    )
    active_subscriptions = result.scalar()
    
    # Calculate revenue (placeholder - would need actual payment data)
    result = await db.execute(
        select(Subscription.plan_id, func.count()).
        where(Subscription.status == "active").
        group_by(Subscription.plan_id)
    )
    plan_counts = dict(result.all())
    
    # Plan prices
    plan_prices = {"starter": 9, "plus": 29, "pro": 99}
    total_revenue = sum(plan_prices.get(plan, 0) * count for plan, count in plan_counts.items())
    
    # Usage stats
    result = await db.execute(
        select(UsageEvent.event_type, func.count()).
        group_by(UsageEvent.event_type)
    )
    usage_by_type = dict(result.all())
    
    # Job stats
    result = await db.execute(
        select(Job.type, Job.status, func.count()).
        group_by(Job.type, Job.status)
    )
    job_stats = {}
    for job_type, job_status, count in result.all():
        if job_type not in job_stats:
            job_stats[job_type] = {}
        job_stats[job_type][job_status] = count
    
    return AnalyticsResponse(
        total_users=total_users,
        active_subscriptions=active_subscriptions,
        total_revenue=total_revenue,
        usage_stats={
            "by_type": usage_by_type,
            "by_plan": plan_counts,
            "jobs": job_stats,
        },
    )

