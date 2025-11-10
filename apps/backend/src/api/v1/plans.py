"""
Plans routes - Subscription plans management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict

from ...core import get_db, get_logger
from ...models import Plan

logger = get_logger(__name__)
router = APIRouter()


# Schemas
class PlanResponse(BaseModel):
    id: str
    name: str
    price_jod: float
    token_limit: int
    image_limit: int
    video_limit: int
    features: Dict


class PlansListResponse(BaseModel):
    plans: List[PlanResponse]
    addons: List[Dict]


# Routes
@router.get("", response_model=PlansListResponse)
async def list_plans(db: Session = Depends(get_db)):
    """
    List all available subscription plans.
    """
    plans = db.query(Plan).all()
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            "id": str(plan.id),
            "name": plan.name,
            "price_jod": float(plan.price_jod),
            "token_limit": plan.token_limit,
            "image_limit": plan.image_limit,
            "video_limit": plan.video_limit,
            "features": plan.features_json or {}
        })
    
    # Add-ons pricing
    addons = [
        {
            "type": "tokens",
            "amount": 200000,
            "price_jod": 1.00
        },
        {
            "type": "images",
            "amount": 10,
            "price_jod": 1.00
        },
        {
            "type": "video",
            "amount": 1,
            "price_jod": 1.00
        }
    ]
    
    return {
        "data": {
            "plans": plans_data,
            "addons": addons
        }
    }


@router.get("/{plan_id}")
async def get_plan(plan_id: str, db: Session = Depends(get_db)):
    """Get details of a specific plan."""
    
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return {
        "data": {
            "id": str(plan.id),
            "name": plan.name,
            "price_jod": float(plan.price_jod),
            "token_limit": plan.token_limit,
            "image_limit": plan.image_limit,
            "video_limit": plan.video_limit,
            "features": plan.features_json or {},
            "description": f"{plan.name} plan with {plan.token_limit} tokens, {plan.image_limit} images, and {plan.video_limit} videos per month"
        }
    }
