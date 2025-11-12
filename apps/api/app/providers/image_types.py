"""Types for image generation."""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ImageProvider(str, Enum):
    """Supported image generation providers."""

    GOOGLE = "google"
    OPENAI = "openai"  # Future support


class ImageSize(str, Enum):
    """Image sizes."""

    SQUARE_256 = "256x256"
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    PORTRAIT = "768x1024"
    LANDSCAPE = "1024x768"


class ImageRequest(BaseModel):
    """Image generation request."""

    prompt: str = Field(..., min_length=1, max_length=1000)
    negative_prompt: Optional[str] = Field(None, max_length=500)
    count: int = Field(1, ge=1, le=4)
    size: ImageSize = ImageSize.SQUARE_1024
    seed: Optional[int] = None
    guidance_scale: Optional[float] = Field(7.5, ge=1.0, le=20.0)


class GeneratedImage(BaseModel):
    """Generated image result."""

    url: str
    s3_key: str
    size: str
    seed: Optional[int] = None


class ImageResponse(BaseModel):
    """Image generation response."""

    job_id: str
    images: List[GeneratedImage]
    provider: str
    model: str
    prompt: str

