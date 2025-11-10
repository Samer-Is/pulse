"""
Slides Maker routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ...core import get_db, get_logger, get_current_user
from ...models import User

logger = get_logger(__name__)
router = APIRouter()


# Schemas
class Slide(BaseModel):
    title: str
    content: str
    order: int
    layout: str = "title-content"  # title-content, two-column, full-image, etc.


class SlidesRequest(BaseModel):
    presentation_title: str
    author: str
    theme: str = "professional"  # professional, modern, minimal, etc.
    slides: List[Slide]
    locale: str = "ar"


@router.post("/generate")
async def generate_slides(
    request: SlidesRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Generate presentation slides from provided data.
    
    This is a simplified stub - in production, this would:
    1. Use AI to enhance content
    2. Generate PowerPoint/PDF using python-pptx or similar
    3. Upload to S3
    4. Return download URL
    """
    try:
        logger.info(f"Slides generation request: user={user.id}, slides_count={len(request.slides)}")
        
        # Stub response
        result = {
            "slides_id": "stub_slides_001",
            "status": "completed",
            "download_url": f"https://s3.amazonaws.com/stubs/{user.id}/presentation.pptx",
            "preview_url": f"https://s3.amazonaws.com/stubs/{user.id}/slides_preview.png",
            "format": "pptx",
            "slide_count": len(request.slides),
            "message": "⚠️ This is a stub! Implement actual slides generation with python-pptx."
        }
        
        logger.info(f"Slides generated (stub): slides_id={result['slides_id']}")
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Slides generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Slides generation failed: {str(e)}"
        )


@router.get("/themes")
async def list_themes():
    """List available presentation themes."""
    
    themes = [
        {
            "id": "professional",
            "name": "Professional",
            "name_ar": "احترافي",
            "preview_url": "https://placeholder.co/800x600/blue/white?text=Professional"
        },
        {
            "id": "modern",
            "name": "Modern",
            "name_ar": "عصري",
            "preview_url": "https://placeholder.co/800x600/purple/white?text=Modern"
        },
        {
            "id": "minimal",
            "name": "Minimal",
            "name_ar": "بسيط",
            "preview_url": "https://placeholder.co/800x600/gray/white?text=Minimal"
        }
    ]
    
    return {"data": {"themes": themes}}

