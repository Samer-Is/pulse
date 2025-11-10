"""
Usage routes - Track and enforce quotas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict

from ...core import get_db, get_logger, get_current_user
from ...models import User, UsageLog

logger = get_logger(__name__)
router = APIRouter()


def get_current_period():
    """Get current billing period (monthly)."""
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    return start, end


@router.get("/me")
async def get_my_usage(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get current user's usage for the billing period.
    
    Returns:
        - Period start/end
        - Plan limits
        - Current usage (tokens, images, videos)
        - Remaining quota
        - Warnings (80% threshold)
    """
    if not user.subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No active subscription"
        )
    
    plan = user.subscription.plan
    period_start, period_end = get_current_period()
    
    # Query usage logs for current period
    usage_logs = db.query(UsageLog).filter(
        UsageLog.user_id == user.id,
        UsageLog.created_at >= period_start,
        UsageLog.created_at <= period_end
    ).all()
    
    # Aggregate usage
    tokens_used = sum(log.tokens_used for log in usage_logs if log.tokens_used)
    images_used = sum(log.images_generated for log in usage_logs if log.images_generated)
    videos_used = sum(log.videos_generated for log in usage_logs if log.videos_generated)
    
    # Calculate remaining
    tokens_remaining = max(0, plan.token_limit - tokens_used)
    images_remaining = max(0, plan.image_limit - images_used)
    videos_remaining = max(0, plan.video_limit - videos_used)
    
    # Calculate percentages
    tokens_percentage = (tokens_used / plan.token_limit * 100) if plan.token_limit > 0 else 0
    images_percentage = (images_used / plan.image_limit * 100) if plan.image_limit > 0 else 0
    videos_percentage = (videos_used / plan.video_limit * 100) if plan.video_limit > 0 else 0
    
    # Check warnings (80% threshold)
    tokens_warning = tokens_percentage >= 80
    images_warning = images_percentage >= 80
    videos_warning = videos_percentage >= 80
    
    return {
        "data": {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "plan": {
                "name": plan.name,
                "limits": {
                    "tokens": plan.token_limit,
                    "images": plan.image_limit,
                    "videos": plan.video_limit
                }
            },
            "usage": {
                "tokens": {
                    "used": tokens_used,
                    "remaining": tokens_remaining,
                    "percentage": round(tokens_percentage, 2)
                },
                "images": {
                    "used": images_used,
                    "remaining": images_remaining,
                    "percentage": round(images_percentage, 2)
                },
                "videos": {
                    "used": videos_used,
                    "remaining": videos_remaining,
                    "percentage": round(videos_percentage, 2)
                }
            },
            "warnings": {
                "tokens": tokens_warning,
                "images": images_warning,
                "videos": videos_warning
            }
        }
    }


@router.post("/log")
async def log_usage(
    resource_type: str,  # "tokens", "images", "videos"
    amount: int,
    metadata: Dict = {},
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Log usage (internal endpoint, called by Gateway).
    
    Args:
        resource_type: Type of resource consumed
        amount: Amount consumed
        metadata: Additional metadata (model, cost, etc.)
    """
    if not user.subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No active subscription"
        )
    
    # Create usage log entry
    log_entry = UsageLog(
        user_id=user.id,
        subscription_id=user.subscription.id,
        resource_type=resource_type,
        amount=amount,
        metadata_json=metadata
    )
    
    if resource_type == "tokens":
        log_entry.tokens_used = amount
    elif resource_type == "images":
        log_entry.images_generated = amount
    elif resource_type == "videos":
        log_entry.videos_generated = amount
    
    db.add(log_entry)
    db.commit()
    
    logger.info(f"Usage logged: user={user.id}, type={resource_type}, amount={amount}")
    
    return {
        "data": {
            "message": "Usage logged successfully"
        }
    }


@router.post("/check")
async def check_quota(
    resource_type: str,
    amount: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Check if user has sufficient quota (pre-flight check).
    
    Args:
        resource_type: Type of resource to consume
        amount: Amount to consume
    
    Returns:
        - allowed: Boolean
        - reason: String (if not allowed)
    """
    if not user.subscription:
        return {
            "data": {
                "allowed": False,
                "reason": "No active subscription"
            }
        }
    
    plan = user.subscription.plan
    period_start, _ = get_current_period()
    
    # Get current usage
    if resource_type == "tokens":
        used = db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.created_at >= period_start
        ).with_entities(db.func.sum(UsageLog.tokens_used)).scalar() or 0
        
        limit = plan.token_limit
    elif resource_type == "images":
        used = db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.created_at >= period_start
        ).with_entities(db.func.sum(UsageLog.images_generated)).scalar() or 0
        
        limit = plan.image_limit
    elif resource_type == "videos":
        used = db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.created_at >= period_start
        ).with_entities(db.func.sum(UsageLog.videos_generated)).scalar() or 0
        
        limit = plan.video_limit
    else:
        return {
            "data": {
                "allowed": False,
                "reason": f"Invalid resource type: {resource_type}"
            }
        }
    
    # Check if would exceed limit
    if used + amount > limit:
        return {
            "data": {
                "allowed": False,
                "reason": f"Quota exceeded. Used: {used}/{limit} {resource_type}",
                "used": used,
                "limit": limit,
                "requested": amount
            }
        }
    
    return {
        "data": {
            "allowed": True,
            "remaining": limit - used - amount
        }
    }
