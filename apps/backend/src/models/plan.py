"""
Plan and Subscription models.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from ..core.db import Base


class Plan(Base):
    """Subscription plan model."""
    
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    price_jod = Column(Numeric(10, 2), nullable=False)
    token_limit = Column(Integer, nullable=False)
    image_limit = Column(Integer, nullable=False)
    video_limit = Column(Integer, nullable=False)
    features_json = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan {self.name} - {self.price_jod} JD>"


class Subscription(Base):
    """User subscription model."""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, active, cancelled, expired
    renews_at = Column(DateTime, nullable=True)
    provider = Column(String(50), nullable=True)  # hyperpay, paytabs, zaincash
    external_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    
    # Indexes
    __table_args__ = (
        Index("ix_subscriptions_user_status", "user_id", "status"),
    )
    
    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.plan.name} - {self.status}>"
