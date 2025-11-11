"""Replicate provider client for image generation (fallback)."""

import httpx
from typing import List, Dict, Any, Optional

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ReplicateClient:
    """Replicate API client for image generation."""
    
    def __init__(self):
        self.api_token = settings.REPLICATE_API_TOKEN
        self.base_url = "https://api.replicate.com/v1"
        self.client = httpx.AsyncClient()
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "stability-ai/stable-diffusion-xl-base-1.0",
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate images using Replicate.
        
        Args:
            prompt: Text description
            model: Replicate model ID
            negative_prompt: What to avoid
            width: Image width
            height: Image height
            num_images: Number of images
        
        Returns:
            Dict with image URLs and metadata
        """
        try:
            logger.info(f"Replicate image generation: prompt='{prompt[:50]}...', model={model}")
            
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "version": model,
                "input": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt or "",
                    "width": width,
                    "height": height,
                    "num_outputs": num_images
                }
            }
            
            # Create prediction
            response = await self.client.post(
                f"{self.base_url}/predictions",
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            prediction = response.json()
            
            prediction_id = prediction["id"]
            
            # Poll for completion
            while prediction["status"] not in ["succeeded", "failed", "canceled"]:
                await asyncio.sleep(1)
                
                response = await self.client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=headers
                )
                prediction = response.json()
            
            if prediction["status"] == "succeeded":
                image_urls = prediction.get("output", [])
                
                result = {
                    "id": prediction_id,
                    "model": model,
                    "images": [
                        {
                            "url": url,
                            "width": width,
                            "height": height
                        }
                        for url in image_urls
                    ],
                    "prompt": prompt,
                    "status": "completed"
                }
                
                logger.info(f"Replicate generation complete: {len(result['images'])} images")
                
                return result
            else:
                raise Exception(f"Replicate generation failed: {prediction['status']}")
            
        except Exception as e:
            logger.error(f"Replicate request failed: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Singleton instance
_replicate_client: Optional[ReplicateClient] = None


def get_replicate_client() -> ReplicateClient:
    """Get or create Replicate client instance."""
    global _replicate_client
    if _replicate_client is None:
        _replicate_client = ReplicateClient()
    return _replicate_client


async def generate_image(**kwargs) -> Dict[str, Any]:
    """Convenience function for image generation."""
    client = get_replicate_client()
    return await client.generate_image(**kwargs)

