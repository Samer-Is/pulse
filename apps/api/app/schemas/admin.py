"""Admin schemas."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UserListResponse(BaseModel):
    """List of users response."""

    users: List[dict]
    total: int
    page: int
    per_page: int


class SubscriptionListResponse(BaseModel):
    """List of subscriptions response."""

    subscriptions: List[dict]
    total: int
    page: int
    per_page: int


class AnalyticsResponse(BaseModel):
    """Analytics response."""

    total_users: int
    active_subscriptions: int
    total_revenue: float
    usage_stats: dict


class UserUpdateRequest(BaseModel):
    """Admin user update request."""

    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class SubscriptionUpdateRequest(BaseModel):
    """Admin subscription update request."""

    plan_id: Optional[str] = None
    status: Optional[str] = None
    period_end: Optional[datetime] = None

