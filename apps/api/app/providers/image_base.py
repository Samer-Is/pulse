"""Base interface for image generation providers."""

from abc import ABC, abstractmethod
from typing import List

from .image_types import ImageRequest, GeneratedImage


class BaseImageProvider(ABC):
    """Abstract base class for image generation providers."""

    def __init__(self, credentials: dict):
        """
        Initialize image provider.
        
        Args:
            credentials: Provider-specific credentials
        """
        self.credentials = credentials

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass

    @abstractmethod
    async def generate_images(
        self,
        request: ImageRequest,
    ) -> List[bytes]:
        """
        Generate images from prompt.
        
        Args:
            request: Image generation request
            
        Returns:
            List of image bytes
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model name used for generation.
        
        Returns:
            Model name
        """
        pass

