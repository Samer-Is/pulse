"""Subscription model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from .base import Base, TimestampMixin


class PlanType(str, Enum):
    """Subscription plan types."""

    STARTER = "starter"
    PLUS = "plus"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Subscription(Base, TimestampMixin):
    """Subscription model for user plans."""

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    
    # Plan details
    plan: Mapped[PlanType] = mapped_column(
        SQLEnum(PlanType), default=PlanType.STARTER, nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False
    )
    
    # Usage tracking (current period)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    images_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    videos_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    slides_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cvs_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Billing period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Stripe integration (optional for future)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan})>"

