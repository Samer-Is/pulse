"""Usage tracking model."""

from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from .job import JobType


class UsageEvent(Base, TimestampMixin):
    """Usage event model for detailed tracking."""

    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="usage_events")

    def __repr__(self) -> str:
        return f"<UsageEvent(id={self.id}, type={self.event_type}, tokens={self.tokens})>"

