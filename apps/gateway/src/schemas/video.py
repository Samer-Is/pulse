"""Video generation schemas."""

from pydantic import BaseModel
from typing import Optional


class VideoGenerateRequest(BaseModel):
    """Video generation request schema."""
    model: str  # veo3:default, pika:1.0, runway:gen-2
    prompt: str
    duration_s: int = 5
    width: int = 1280
    height: int = 720
    fps: int = 30


class VideoGenerateResponse(BaseModel):
    """Video generation response schema."""
    id: str
    model: str
    video_url: str
    thumbnail_url: Optional[str] = None
    prompt: str
    duration: int
    width: int
    height: int
    fps: int
    status: str  # queued, processing, completed, failed

