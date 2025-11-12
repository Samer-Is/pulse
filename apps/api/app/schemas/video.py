"""Video generation schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class VideoProvider(str, Enum):
    """Supported video generation providers."""

    RUNWAY = "runway"
    PIKA = "pika"


class VideoGenerationRequest(BaseModel):
    """Video generation request schema."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Text prompt for video generation"
    )
    provider: VideoProvider = Field(
        VideoProvider.RUNWAY,
        description="Video provider: runway or pika"
    )
    duration: int = Field(
        4,
        ge=2,
        le=10,
        description="Video duration in seconds"
    )
    style: Optional[str] = Field(
        None,
        description="Video style or preset"
    )
    aspect_ratio: Optional[str] = Field(
        "16:9",
        description="Aspect ratio (16:9, 9:16, 1:1)"
    )


class VideoGenerationResponse(BaseModel):
    """Video generation response schema."""

    job_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None


class VideoJobStatus(BaseModel):
    """Video job status response."""

    job_id: str
    status: str
    progress: Optional[int] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

