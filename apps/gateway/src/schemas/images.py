"""Image generation schemas."""

from pydantic import BaseModel
from typing import List, Optional


class ImageGenerateRequest(BaseModel):
    """Image generation request schema."""
    model: str  # nano-banana:default, replicate:stable-diffusion-xl
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    count: int = 1


class GeneratedImage(BaseModel):
    """Single generated image."""
    url: str
    width: int
    height: int


class ImageGenerateResponse(BaseModel):
    """Image generation response schema."""
    id: str
    model: str
    images: List[GeneratedImage]
    prompt: str
    status: str

