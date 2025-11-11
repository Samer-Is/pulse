"""Plan schemas."""

from pydantic import BaseModel
from decimal import Decimal
from typing import Dict, Any


class PlanResponse(BaseModel):
    """Response schema for a subscription plan."""
    id: str
    name: str
    price_jod: Decimal
    token_limit: int
    image_limit: int
    video_limit: int
    features_json: Dict[str, Any]
    
    class Config:
        from_attributes = True


class PlansListResponse(BaseModel):
    """Response schema for list of plans."""
    plans: list[PlanResponse]

