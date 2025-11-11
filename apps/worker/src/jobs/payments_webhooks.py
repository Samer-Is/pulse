"""Payment webhook processing job."""

import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta

# Note: In production, import from backend services
# For now, this is a standalone worker


async def process_hyperpay_webhook(payload: Dict[str, Any]) -> bool:
    """
    Process HyperPay payment webhook.
    
    Args:
        payload: Webhook payload from HyperPay
    
    Returns:
        True if processed successfully
    """
    print(f"[Worker] Processing HyperPay webhook: {payload.get('id')}")
    
    try:
        # Extract payment details
        checkout_id = payload.get('id')
        result_code = payload.get('result', {}).get('code')
        user_id = payload.get('customParameters', {}).get('user_id')
        plan_id = payload.get('customParameters', {}).get('plan_id')
        
        # Check if payment successful
        is_successful = result_code == '000.100.110'
        
        if is_successful:
            # Update subscription to active
            # In production: call backend API or update DB directly
            print(f"[Worker] Payment successful: user={user_id}, plan={plan_id}")
            
            # Set renews_at to 30 days from now
            renews_at = datetime.utcnow() + timedelta(days=30)
            
            # TODO: Update database
            # await db.execute(
            #     "UPDATE subscriptions SET status='active', renews_at=? WHERE user_id=?",
            #     (renews_at, user_id)
            # )
            
            print(f"[Worker] Subscription activated: renews_at={renews_at}")
            
        else:
            print(f"[Worker] Payment failed: result_code={result_code}")
        
        return True
        
    except Exception as e:
        print(f"[Worker] Failed to process webhook: {str(e)}")
        return False


async def process_paytabs_webhook(payload: Dict[str, Any]) -> bool:
    """Process PayTabs webhook (stub)."""
    print(f"[Worker] Processing PayTabs webhook (stub)")
    return True


async def process_zaincash_webhook(payload: Dict[str, Any]) -> bool:
    """Process ZainCash webhook (stub)."""
    print(f"[Worker] Processing ZainCash webhook (stub)")
    return True

