"""Content moderation middleware (stub)."""

from typing import Optional
from ..core.logging import get_logger

logger = get_logger(__name__)


class ContentModerator:
    """
    Content moderation service.
    
    ⚠️ This is a STUB implementation.
    Integrate with actual moderation API (OpenAI Moderation, etc.) when ready.
    """
    
    async def moderate_text(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Moderate text content.
        
        Returns:
            (is_safe, reason) tuple
        """
        # Stub: Basic keyword blocking
        blocked_keywords = ["spam", "abuse", "hack"]
        
        text_lower = text.lower()
        for keyword in blocked_keywords:
            if keyword in text_lower:
                logger.warning(f"Content blocked: keyword={keyword}")
                return (False, f"Content contains blocked keyword: {keyword}")
        
        return (True, None)
    
    async def moderate_image_prompt(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Moderate image generation prompt.
        
        Returns:
            (is_safe, reason) tuple
        """
        # Stub: Use same logic as text
        return await self.moderate_text(prompt)
    
    async def moderate_video_prompt(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Moderate video generation prompt.
        
        Returns:
            (is_safe, reason) tuple
        """
        # Stub: Use same logic as text
        return await self.moderate_text(prompt)


# Global moderator instance
moderator = ContentModerator()

