"""
CV Maker routes.
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
class CVSection(BaseModel):
    type: str  # education, experience, skills, etc.
    title: str
    content: str
    order: int


class CVRequest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    title: str  # Job title
    summary: str
    sections: List[CVSection]
    locale: str = "ar"  # ar or en


@router.post("/generate")
async def generate_cv(
    request: CVRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Generate CV from provided data.
    
    This is a simplified stub - in production, this would:
    1. Use AI to enhance/format content
    2. Generate PDF using a template engine
    3. Upload to S3
    4. Return download URL
    """
    try:
        logger.info(f"CV generation request: user={user.id}, locale={request.locale}")
        
        # Stub response
        result = {
            "cv_id": "stub_cv_001",
            "status": "completed",
            "download_url": f"https://s3.amazonaws.com/stubs/{user.id}/cv.pdf",
            "preview_url": f"https://s3.amazonaws.com/stubs/{user.id}/cv_preview.png",
            "format": "pdf",
            "message": "⚠️ This is a stub! Implement actual CV generation with PDF template engine."
        }
        
        logger.info(f"CV generated (stub): cv_id={result['cv_id']}")
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"CV generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV generation failed: {str(e)}"
        )


@router.get("/templates")
async def list_cv_templates():
    """List available CV templates."""
    
    templates = [
        {
            "id": "professional",
            "name": "Professional",
            "name_ar": "احترافي",
            "preview_url": "https://placeholder.co/400x600/blue/white?text=Professional"
        },
        {
            "id": "modern",
            "name": "Modern",
            "name_ar": "عصري",
            "preview_url": "https://placeholder.co/400x600/green/white?text=Modern"
        },
        {
            "id": "classic",
            "name": "Classic",
            "name_ar": "كلاسيكي",
            "preview_url": "https://placeholder.co/400x600/gray/white?text=Classic"
        }
    ]
    
    return {"data": {"templates": templates}}

