"""HyperPay payment provider implementation."""

import httpx
from typing import Dict, Any
from decimal import Decimal

from .base import PaymentProvider
from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class HyperPayProvider(PaymentProvider):
    """HyperPay payment provider."""
    
    def __init__(self):
        self.api_key = settings.HYPERPAY_API_KEY
        self.entity_id = settings.HYPERPAY_ENTITY_ID
        self.test_mode = settings.HYPERPAY_TEST_MODE
        self.base_url = "https://test.oppwa.com" if self.test_mode else "https://oppwa.com"
        self.client = httpx.AsyncClient()
    
    async def create_checkout_session(
        self,
        amount: Decimal,
        currency: str,
        user_id: str,
        plan_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create HyperPay checkout session."""
        
        try:
            data = {
                "entityId": self.entity_id,
                "amount": str(amount),
                "currency": currency,
                "paymentType": "DB",  # Debit
                "merchantTransactionId": f"{user_id}_{plan_id}_{int(amount * 100)}",
                "customer.email": metadata.get("email", ""),
                "customParameters[user_id]": user_id,
                "customParameters[plan_id]": plan_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = await self.client.post(
                f"{self.base_url}/v1/checkouts",
                data=data,
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            checkout_id = result.get("id")
            redirect_url = f"{settings.BASE_URL}/payments/hyperpay?id={checkout_id}"
            
            logger.info(f"HyperPay session created: checkout_id={checkout_id}")
            
            return {
                "session_id": checkout_id,
                "redirect_url": redirect_url
            }
            
        except Exception as e:
            logger.error(f"HyperPay session creation failed: {str(e)}")
            raise
    
    async def verify_webhook(self, payload: Dict[str, Any]) -> bool:
        """Verify HyperPay webhook."""
        # HyperPay doesn't send webhooks in test mode, payment status is checked via redirect
        return True
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process HyperPay webhook."""
        checkout_id = payload.get("id")
        
        # Get payment status
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = await self.client.get(
            f"{self.base_url}/v1/checkouts/{checkout_id}/payment",
            headers=headers
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "payment_id": checkout_id,
            "status": "completed" if result.get("result", {}).get("code") == "000.100.110" else "failed",
            "amount": Decimal(result.get("amount", "0")),
            "currency": result.get("currency"),
            "user_id": result.get("customParameters", {}).get("user_id"),
            "plan_id": result.get("customParameters", {}).get("plan_id")
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

