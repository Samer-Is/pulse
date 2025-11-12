"""Stripe payment service."""

import os
from typing import Optional
from datetime import datetime, timedelta
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user import User
from ..models.subscription import Subscription


class StripeService:
    """Handle Stripe payment operations."""

    def __init__(self):
        """Initialize Stripe service."""
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        if self.api_key:
            stripe.api_key = self.api_key
        
        # Plan price IDs (should be set in environment or config)
        self.price_ids = {
            "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter"),
            "plus": os.getenv("STRIPE_PRICE_PLUS", "price_plus"),
            "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro"),
        }

    async def create_checkout_session(
        self,
        user: User,
        plan_id: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create Stripe checkout session for subscription.
        
        Args:
            user: Current user
            plan_id: Plan ID (starter, plus, pro)
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            
        Returns:
            Session ID and URL
        """
        if plan_id not in self.price_ids:
            raise ValueError(f"Invalid plan_id: {plan_id}")
        
        # Get or create Stripe customer
        customer_id = user.stripe_customer_id
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": user.id},
            )
            customer_id = customer.id
            # Note: Update user.stripe_customer_id in database after this
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": self.price_ids[plan_id],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "plan_id": plan_id,
            },
        )
        
        return {
            "session_id": session.id,
            "url": session.url,
            "customer_id": customer_id,
        }

    async def create_portal_session(
        self,
        user: User,
        return_url: str,
    ) -> dict:
        """
        Create Stripe customer portal session.
        
        Args:
            user: Current user
            return_url: Return URL after portal
            
        Returns:
            Portal URL
        """
        if not user.stripe_customer_id:
            raise ValueError("User has no Stripe customer ID")
        
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )
        
        return {"url": session.url}

    async def handle_checkout_completed(
        self,
        session: dict,
        db: AsyncSession,
    ) -> None:
        """
        Handle successful checkout completion.
        
        Args:
            session: Stripe session object
            db: Database session
        """
        user_id = session["metadata"]["user_id"]
        plan_id = session["metadata"]["plan_id"]
        customer_id = session["customer"]
        subscription_id = session["subscription"]
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        # Update user's Stripe customer ID
        if not user.stripe_customer_id:
            user.stripe_customer_id = customer_id
        
        # Get subscription details from Stripe
        stripe_sub = stripe.Subscription.retrieve(subscription_id)
        
        # Create or update subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Update existing subscription
            subscription.plan_id = plan_id
            subscription.stripe_subscription_id = subscription_id
            subscription.status = "active"
            subscription.period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
            subscription.period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=subscription_id,
                status="active",
                period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
                period_end=datetime.fromtimestamp(stripe_sub.current_period_end),
            )
            db.add(subscription)
        
        await db.commit()

    async def handle_subscription_updated(
        self,
        subscription_data: dict,
        db: AsyncSession,
    ) -> None:
        """
        Handle subscription update event.
        
        Args:
            subscription_data: Stripe subscription object
            db: Database session
        """
        stripe_sub_id = subscription_data["id"]
        
        # Find subscription
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return
        
        # Update subscription
        subscription.status = subscription_data["status"]
        subscription.period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
        subscription.period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
        
        # Reset usage counters if period renewed
        if subscription_data.get("status") == "active":
            # Check if it's a new period (compare timestamps)
            pass  # Usage reset will be handled by a background job
        
        await db.commit()

    async def handle_subscription_deleted(
        self,
        subscription_data: dict,
        db: AsyncSession,
    ) -> None:
        """
        Handle subscription cancellation.
        
        Args:
            subscription_data: Stripe subscription object
            db: Database session
        """
        stripe_sub_id = subscription_data["id"]
        
        # Find subscription
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return
        
        # Update subscription status
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        
        await db.commit()

    async def cancel_subscription(
        self,
        user: User,
        db: AsyncSession,
    ) -> None:
        """
        Cancel user's subscription.
        
        Args:
            user: Current user
            db: Database session
        """
        # Get subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription or not subscription.stripe_subscription_id:
            raise ValueError("No active subscription found")
        
        # Cancel in Stripe
        stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Update in database
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        
        await db.commit()


def get_stripe_service() -> StripeService:
    """Get Stripe service instance."""
    return StripeService()

