"""
Image generation routes.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from ..core.logging import get_logger
from ..providers import nano_banana_stub

logger = get_logger(__name__)
router = APIRouter()


# Schemas
class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    num_images: int = 1


@router.post("/generate")
async def generate_image(request: ImageGenerationRequest):
    """
    Generate images using Nano Banana.
    
    ⚠️ Currently using STUB implementation!
    """
    try:
        logger.info(f"Image generation request: prompt='{request.prompt[:50]}...'")
        
        result = await nano_banana_stub.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_images=request.num_images
        )
        
        logger.info(f"Image generation successful: {len(result['images'])} images")
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )
