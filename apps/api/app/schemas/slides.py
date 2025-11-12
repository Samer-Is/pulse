"""Slide generation schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field


class SlideContent(BaseModel):
    """Individual slide content."""

    title: str = Field(..., min_length=1, max_length=200)
    content: List[str] = Field(..., description="List of bullet points or paragraphs")
    notes: Optional[str] = Field(None, max_length=500, description="Speaker notes")


class SlideGenerationRequest(BaseModel):
    """Slide generation request."""

    topic: Optional[str] = Field(None, max_length=200, description="Topic for AI-generated outline")
    outline: Optional[List[SlideContent]] = Field(None, description="Manual slide outline")
    auto_generate: bool = Field(False, description="Use AI to generate slides from topic")
    num_slides: Optional[int] = Field(5, ge=3, le=20, description="Number of slides for auto-generation")
    template: Optional[str] = Field("modern", description="Template style: modern, classic, minimal")
    format: str = Field("pptx", description="Export format: pptx or pdf")


class SlideGenerationResponse(BaseModel):
    """Slide generation response."""

    job_id: str
    format: str
    download_url: str
    s3_key: str
    slide_count: int
    expires_at: str


class OutlineGenerationRequest(BaseModel):
    """Request for AI-generated outline."""

    topic: str = Field(..., min_length=5, max_length=200)
    num_slides: int = Field(5, ge=3, le=20)
    audience: Optional[str] = Field(None, max_length=100, description="Target audience")
    style: Optional[str] = Field(None, max_length=50, description="Presentation style")


class OutlineGenerationResponse(BaseModel):
    """AI-generated outline response."""

    topic: str
    slides: List[SlideContent]

