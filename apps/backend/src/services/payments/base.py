"""Base payment provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from decimal import Decimal


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    @abstractmethod
    async def create_checkout_session(
        self,
        amount: Decimal,
        currency: str,
        user_id: str,
        plan_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Create a checkout session.
        
        Returns:
            Dict with session_id and redirect_url
        """
        pass
    
    @abstractmethod
    async def verify_webhook(self, payload: Dict[str, Any]) -> bool:
        """
        Verify webhook authenticity.
        
        Returns:
            True if webhook is valid
        """
        pass
    
    @abstractmethod
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook payload.
        
        Returns:
            Dict with payment details
        """
        pass

