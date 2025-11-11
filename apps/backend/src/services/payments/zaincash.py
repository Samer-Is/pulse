"""ZainCash payment provider stub."""

from typing import Dict, Any
from decimal import Decimal

from .base import PaymentProvider
from ...core.logging import get_logger

logger = get_logger(__name__)


class ZainCashProvider(PaymentProvider):
    """
    ZainCash payment provider (STUB).
    
    ⚠️ This is a placeholder implementation.
    Integrate with actual ZainCash API when ready.
    """
    
    async def create_checkout_session(
        self,
        amount: Decimal,
        currency: str,
        user_id: str,
        plan_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create ZainCash checkout session (stub)."""
        logger.warning("⚠️ Using ZainCash STUB! Implement real integration.")
        
        return {
            "session_id": "zaincash_stub_session_001",
            "redirect_url": "https://stub.zaincash.iq/checkout"
        }
    
    async def verify_webhook(self, payload: Dict[str, Any]) -> bool:
        """Verify ZainCash webhook (stub)."""
        return True
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process ZainCash webhook (stub)."""
        return {
            "payment_id": "zaincash_stub_001",
            "status": "completed",
            "amount": Decimal("3.00"),
            "currency": "JOD"
        }

