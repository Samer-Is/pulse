"""Subscription schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ..models.subscription import PlanType, SubscriptionStatus


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""

    id: str
    user_id: str
    plan: PlanType
    status: SubscriptionStatus
    tokens_used: int
    images_generated: int
    videos_generated: int
    slides_generated: int
    cvs_generated: int
    period_start: datetime
    period_end: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

