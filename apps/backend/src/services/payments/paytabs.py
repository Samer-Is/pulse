"""PayTabs payment provider stub."""

from typing import Dict, Any
from decimal import Decimal

from .base import PaymentProvider
from ...core.logging import get_logger

logger = get_logger(__name__)


class PayTabsProvider(PaymentProvider):
    """
    PayTabs payment provider (STUB).
    
    ⚠️ This is a placeholder implementation.
    Integrate with actual PayTabs API when ready.
    """
    
    async def create_checkout_session(
        self,
        amount: Decimal,
        currency: str,
        user_id: str,
        plan_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create PayTabs checkout session (stub)."""
        logger.warning("⚠️ Using PayTabs STUB! Implement real integration.")
        
        return {
            "session_id": "paytabs_stub_session_001",
            "redirect_url": "https://stub.paytabs.com/checkout"
        }
    
    async def verify_webhook(self, payload: Dict[str, Any]) -> bool:
        """Verify PayTabs webhook (stub)."""
        return True
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayTabs webhook (stub)."""
        return {
            "payment_id": "paytabs_stub_001",
            "status": "completed",
            "amount": Decimal("5.00"),
            "currency": "JOD"
        }

