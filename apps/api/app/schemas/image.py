"""Image generation schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field

from ..providers.image_types import ImageSize


class ImageGenerationRequest(BaseModel):
    """Image generation request schema."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt for image generation"
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="Negative prompt (what to avoid)"
    )
    provider: str = Field(
        "google",
        description="Provider: google (Imagen) or openai (future)"
    )
    count: int = Field(
        1,
        ge=1,
        le=4,
        description="Number of images to generate"
    )
    size: ImageSize = Field(
        ImageSize.SQUARE_1024,
        description="Image size"
    )
    seed: Optional[int] = Field(
        None,
        description="Random seed for reproducibility"
    )
    guidance_scale: Optional[float] = Field(
        7.5,
        ge=1.0,
        le=20.0,
        description="How closely to follow the prompt"
    )


class GeneratedImageInfo(BaseModel):
    """Generated image information."""

    url: str
    s3_key: str
    size: str
    seed: Optional[int] = None


class ImageGenerationResponse(BaseModel):
    """Image generation response schema."""

    job_id: str
    images: List[GeneratedImageInfo]
    provider: str
    model: str
    prompt: str
    count: int


class ImageModelsResponse(BaseModel):
    """Available image models response."""

    models: List[dict]

