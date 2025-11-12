"""Stripe payment routes."""

import os
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.user import User
from ..auth.dependencies import require_auth
from ..schemas.stripe import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionRequest,
    PortalSessionResponse,
)
from ..services.stripe_service import get_stripe_service

router = APIRouter()


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe checkout session for subscription purchase.
    
    Args:
        request: Checkout session request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Checkout session URL
    """
    stripe_service = get_stripe_service()
    
    # Default URLs
    success_url = request.success_url or "http://localhost:3000/dashboard?success=true"
    cancel_url = request.cancel_url or "http://localhost:3000/pricing?cancelled=true"
    
    try:
        result = await stripe_service.create_checkout_session(
            user=current_user,
            plan_id=request.plan_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Update user's Stripe customer ID if created
        if result.get("customer_id") and not current_user.stripe_customer_id:
            current_user.stripe_customer_id = result["customer_id"]
            await db.commit()
        
        return CheckoutSessionResponse(
            session_id=result["session_id"],
            url=result["url"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.post("/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: User = Depends(require_auth),
):
    """
    Create Stripe customer portal session.
    
    Args:
        request: Portal session request
        current_user: Current authenticated user
        
    Returns:
        Portal session URL
    """
    stripe_service = get_stripe_service()
    
    # Default return URL
    return_url = request.return_url or "http://localhost:3000/dashboard"
    
    try:
        result = await stripe_service.create_portal_session(
            user=current_user,
            return_url=return_url,
        )
        
        return PortalSessionResponse(url=result["url"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}",
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """
    Handle Stripe webhook events.
    
    Args:
        request: FastAPI request
        db: Database session
        stripe_signature: Stripe signature header
        
    Returns:
        Success response
    """
    stripe_service = get_stripe_service()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Get raw body
    payload = await request.body()
    
    # Verify signature if webhook secret is configured
    if webhook_secret and stripe_signature:
        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, webhook_secret
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid signature: {str(e)}",
            )
    else:
        # Development mode - parse JSON directly (not recommended for production)
        import json
        event = json.loads(payload)
    
    # Handle different event types
    event_type = event["type"]
    
    try:
        if event_type == "checkout.session.completed":
            await stripe_service.handle_checkout_completed(event["data"]["object"], db)
        
        elif event_type == "customer.subscription.updated":
            await stripe_service.handle_subscription_updated(event["data"]["object"], db)
        
        elif event_type == "customer.subscription.deleted":
            await stripe_service.handle_subscription_deleted(event["data"]["object"], db)
        
        # Add more event handlers as needed
        # - invoice.payment_succeeded
        # - invoice.payment_failed
        # - customer.subscription.trial_will_end
        
        return {"status": "success"}
    
    except Exception as e:
        # Log error but return 200 to prevent Stripe from retrying
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

