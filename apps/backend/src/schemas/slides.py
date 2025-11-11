"""Slides generation schemas."""

from pydantic import BaseModel
from typing import List, Optional


class SlideContent(BaseModel):
    """Individual slide content."""
    title: str
    content: str
    layout: str = "title-content"
    order: int


class SlidesGenerateRequest(BaseModel):
    """Request schema for slides generation."""
    presentation_title: str
    author: str
    topic: str
    audience: str
    num_slides: int
    slides: List[SlideContent]
    theme: str = "professional"
    locale: str = "ar"
    export_format: str = "pptx"  # pptx or pdf


class SlidesGenerateResponse(BaseModel):
    """Response schema for slides generation."""
    slides_id: str
    status: str
    download_url: str
    preview_url: Optional[str] = None
    format: str
    slide_count: int

