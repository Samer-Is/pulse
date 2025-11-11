"""Payment schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PaymentSessionRequest(BaseModel):
    """Request schema for creating payment session."""
    plan_id: str
    provider: str = "hyperpay"


class PaymentSessionResponse(BaseModel):
    """Response schema for payment session."""
    session_id: str
    redirect_url: str
    amount: Decimal
    currency: str = "JOD"


class HyperPayWebhookPayload(BaseModel):
    """Schema for HyperPay webhook payload."""
    id: str
    paymentType: str
    amount: str
    currency: str
    descriptor: str
    result: dict
    customer: Optional[dict] = None
    customParameters: Optional[dict] = None

