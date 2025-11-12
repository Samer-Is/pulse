"""Job model for AI generation tasks."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from .base import Base, TimestampMixin


class JobType(str, Enum):
    """Job types for different AI generation tasks."""

    CHAT = "chat"
    IMAGE = "image"
    VIDEO = "video"
    SLIDES = "slides"
    CV = "cv"


class JobStatus(str, Enum):
    """Job processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base, TimestampMixin):
    """Job model for tracking AI generation tasks."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Job details
    type: Mapped[JobType] = mapped_column(SQLEnum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True
    )
    
    # Input/Output
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    result_url: Mapped[Optional[str]] = mapped_column(String(500))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Processing metadata
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Model used
    model_name: Mapped[Optional[str]] = mapped_column(String(100))
    tokens_used: Mapped[Optional[int]] = mapped_column(default=0)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"

