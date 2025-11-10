"""
Async job model for video generation, etc.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from ..core.db import Base


class Job(Base):
    """Async job model for long-running tasks."""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    kind = Column(String(50), nullable=False)  # video_gen, video_edit
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    payload_json = Column(JSONB, default={})
    result_file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    result_file = relationship("File")
    
    # Indexes
    __table_args__ = (
        Index("ix_jobs_status_created", "status", "created_at"),
        Index("ix_jobs_user_status", "user_id", "status"),
    )
    
    def __repr__(self):
        return f"<Job {self.kind} - {self.status}>"

