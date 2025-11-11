"""Usage schemas."""

from pydantic import BaseModel
from typing import Optional


class UsageLogRequest(BaseModel):
    """Request schema for logging usage."""
    resource_type: str  # tokens, images, videos
    amount: int
    model: Optional[str] = None
    metadata: Optional[dict] = {}


class UsageSummaryResponse(BaseModel):
    """Response schema for user usage summary."""
    user_id: str
    plan_name: str
    token_limit: int
    tokens_used: int
    token_percentage: float
    image_limit: int
    images_used: int
    image_percentage: float
    video_limit: int
    videos_used: int
    video_percentage: float
    quota_warnings: list[str]

