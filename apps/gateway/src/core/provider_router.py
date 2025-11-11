"""Provider routing logic based on model prefix."""

from typing import Dict, Any, Callable
from ..core.logging import get_logger

logger = get_logger(__name__)


class ProviderRouter:
    """Route requests to appropriate provider based on model name."""
    
    def __init__(self):
        self.chat_providers = {}
        self.image_providers = {}
        self.video_providers = {}
    
    def register_chat_provider(self, prefix: str, handler: Callable):
        """Register a chat provider."""
        self.chat_providers[prefix] = handler
        logger.info(f"Registered chat provider: {prefix}")
    
    def register_image_provider(self, prefix: str, handler: Callable):
        """Register an image provider."""
        self.image_providers[prefix] = handler
        logger.info(f"Registered image provider: {prefix}")
    
    def register_video_provider(self, prefix: str, handler: Callable):
        """Register a video provider."""
        self.video_providers[prefix] = handler
        logger.info(f"Registered video provider: {prefix}")
    
    def route_chat(self, model: str) -> Callable:
        """Route chat request to appropriate provider."""
        prefix = model.split(':')[0] if ':' in model else 'openai'
        
        provider = self.chat_providers.get(prefix)
        if not provider:
            logger.warning(f"No provider found for prefix: {prefix}, using openai")
            provider = self.chat_providers.get('openai')
        
        return provider
    
    def route_image(self, model: str) -> Callable:
        """Route image request to appropriate provider."""
        prefix = model.split(':')[0] if ':' in model else 'nano-banana'
        
        provider = self.image_providers.get(prefix)
        if not provider:
            logger.warning(f"No provider found for prefix: {prefix}, using nano-banana")
            provider = self.image_providers.get('nano-banana')
        
        return provider
    
    def route_video(self, model: str) -> Callable:
        """Route video request to appropriate provider."""
        prefix = model.split(':')[0] if ':' in model else 'veo3'
        
        provider = self.video_providers.get(prefix)
        if not provider:
            logger.warning(f"No provider found for prefix: {prefix}, using veo3")
            provider = self.video_providers.get('veo3')
        
        return provider


# Global router instance
router = ProviderRouter()

