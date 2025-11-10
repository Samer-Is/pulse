"""
File storage model.
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from ..core.db import Base


class File(Base):
    """File storage model for images, videos, documents."""
    
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    kind = Column(String(50), nullable=False)  # image, video, doc
    s3_key = Column(String(500), nullable=False)
    bytes = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_json = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="files")
    
    # Indexes
    __table_args__ = (
        Index("ix_files_user_created", "user_id", "created_at"),
        Index("ix_files_kind", "kind"),
    )
    
    def __repr__(self):
        return f"<File {self.kind} - {self.s3_key}>"
