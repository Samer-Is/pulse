"""
Payment model.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from ..core.db import Base


class Payment(Base):
    """Payment transaction model."""
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    amount_jod = Column(Numeric(10, 2), nullable=False)
    provider = Column(String(50), nullable=False)  # hyperpay, paytabs, zaincash
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed, refunded
    external_id = Column(String(255), nullable=True, index=True)  # Provider's transaction ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_json = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index("ix_payments_user_created", "user_id", "created_at"),
        Index("ix_payments_status", "status"),
    )
    
    def __repr__(self):
        return f"<Payment {self.amount_jod} JD - {self.status}>"
