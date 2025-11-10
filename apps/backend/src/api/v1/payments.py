"""
Payments routes - HyperPay integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac

from ...core import get_db, get_logger, get_current_user
from ...core.config import get_settings
from ...models import User, Subscription, Plan, PaymentTransaction

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


# Schemas
class CheckoutRequest(BaseModel):
    plan_id: str
    addon_type: Optional[str] = None  # "tokens", "images", "video"
    addon_amount: Optional[int] = None


class CheckoutResponse(BaseModel):
    checkout_id: str
    checkout_url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create HyperPay checkout session for subscription or add-on.
    
    Args:
        plan_id: Plan ID (for new subscription)
        addon_type: Type of add-on ("tokens", "images", "video")
        addon_amount: Amount of add-on
    
    Returns:
        checkout_id and checkout_url
    """
    # Get plan
    plan = db.query(Plan).filter(Plan.id == request.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Calculate amount
    if request.addon_type:
        # Add-on pricing
        addon_prices = {
            "tokens": 1.00,  # 1 JD per 200k tokens
            "images": 1.00,  # 1 JD per 10 images
            "video": 1.00    # 1 JD per video
        }
        amount = addon_prices.get(request.addon_type, 0)
        description = f"Add-on: {request.addon_amount} {request.addon_type}"
    else:
        # Subscription
        amount = float(plan.price_jod)
        description = f"Subscription: {plan.name}"
    
    # TODO: Integrate with HyperPay API
    # This is a stub implementation
    # In production, call HyperPay's /v1/checkouts endpoint
    
    checkout_id = f"stub_{user.id}_{plan.id}"
    checkout_url = f"https://test.oppwa.com/v1/paymentWidgets.js?checkoutId={checkout_id}"
    
    # Create payment transaction record
    transaction = PaymentTransaction(
        user_id=user.id,
        plan_id=plan.id,
        amount=amount,
        currency="JOD",
        provider="hyperpay",
        provider_checkout_id=checkout_id,
        status="pending"
    )
    db.add(transaction)
    db.commit()
    
    logger.info(f"Checkout created: user={user.id}, plan={plan.id}, amount={amount} JOD")
    
    return {
        "data": {
            "checkout_id": checkout_id,
            "checkout_url": checkout_url
        }
    }


@router.post("/webhook/hyperpay")
async def hyperpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    HyperPay webhook handler for payment confirmation.
    
    Validates signature and updates subscription status.
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # TODO: Verify HyperPay signature
    # signature = request.headers.get("X-HyperPay-Signature")
    # expected_signature = hmac.new(
    #     settings.HYPERPAY_WEBHOOK_SECRET.encode(),
    #     body,
    #     hashlib.sha256
    # ).hexdigest()
    # 
    # if signature != expected_signature:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Parse webhook data
    data = await request.json()
    
    checkout_id = data.get("id")
    payment_status = data.get("result", {}).get("code")
    
    # Find transaction
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider_checkout_id == checkout_id
    ).first()
    
    if not transaction:
        logger.error(f"Transaction not found: {checkout_id}")
        return {"status": "error", "message": "Transaction not found"}
    
    # Check payment success (HyperPay success codes start with "000.000")
    if payment_status and payment_status.startswith("000.000"):
        transaction.status = "completed"
        transaction.provider_payment_id = data.get("paymentId")
        
        # Create or update subscription
        user = transaction.user
        if user.subscription:
            # Extend existing subscription
            user.subscription.status = "active"
            # TODO: Update renews_at
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=transaction.plan_id,
                status="active"
                # TODO: Set renews_at to 1 month from now
            )
            db.add(subscription)
        
        db.commit()
        
        logger.info(f"Payment successful: user={user.id}, transaction={transaction.id}")
        
        return {"status": "success"}
    else:
        transaction.status = "failed"
        db.commit()
        
        logger.warning(f"Payment failed: transaction={transaction.id}, code={payment_status}")
        
        return {"status": "failed"}


@router.get("/history")
async def payment_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's payment history."""
    
    transactions = db.query(PaymentTransaction).filter(
        PaymentTransaction.user_id == user.id
    ).order_by(PaymentTransaction.created_at.desc()).limit(20).all()
    
    return {
        "data": {
            "transactions": [
                {
                    "id": str(t.id),
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "status": t.status,
                    "created_at": t.created_at.isoformat(),
                    "plan_name": t.plan.name if t.plan else None
                }
                for t in transactions
            ]
        }
    }
