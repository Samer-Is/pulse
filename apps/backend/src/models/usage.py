"""
Usage tracking model.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from ..core.db import Base


class UsageLog(Base):
    """Usage log model for tracking token/image/video consumption."""
    
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    resource_type = Column(String(50), nullable=False)  # tokens, images, videos
    amount = Column(Integer, nullable=False)
    tokens_used = Column(Integer, nullable=True)  # For chat
    images_generated = Column(Integer, nullable=True)  # For images
    videos_generated = Column(Integer, nullable=True)  # For videos
    model = Column(String(100), nullable=True)  # gpt-4o, nano-banana, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata_json = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    
    # Indexes
    __table_args__ = (
        Index("ix_usage_user_created", "user_id", "created_at"),
        Index("ix_usage_resource_created", "resource_type", "created_at"),
        Index("ix_usage_model", "model"),
    )
    
    def __repr__(self):
        return f"<UsageLog {self.resource_type} - {self.amount} by {self.user_id}>"
