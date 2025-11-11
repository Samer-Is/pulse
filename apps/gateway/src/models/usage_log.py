"""Usage log model for gateway."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UsageLog(BaseModel):
    """Usage log entry."""
    user_id: str
    resource_type: str  # tokens, images, videos
    amount: int
    model: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    metadata: dict = {}
    
    class Config:
        from_attributes = True

