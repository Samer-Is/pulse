"""Stripe payment schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class CheckoutSessionRequest(BaseModel):
    """Request to create Stripe checkout session."""

    plan_id: str = Field(..., description="Plan ID: starter, plus, or pro")
    success_url: Optional[str] = Field(None, description="Redirect URL on success")
    cancel_url: Optional[str] = Field(None, description="Redirect URL on cancel")


class CheckoutSessionResponse(BaseModel):
    """Stripe checkout session response."""

    session_id: str
    url: str


class PortalSessionRequest(BaseModel):
    """Request to create Stripe customer portal session."""

    return_url: Optional[str] = Field(None, description="Return URL after portal")


class PortalSessionResponse(BaseModel):
    """Stripe customer portal session response."""

    url: str


class WebhookEvent(BaseModel):
    """Stripe webhook event."""

    type: str
    data: dict

