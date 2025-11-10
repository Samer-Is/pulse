"""
Video generation routes.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..core.logging import get_logger
from ..providers import veo3_stub

logger = get_logger(__name__)
router = APIRouter()


# Schemas
class VideoGenerationRequest(BaseModel):
    prompt: str
    duration: int = 5
    width: int = 1280
    height: int = 720
    fps: int = 30


@router.post("/generate")
async def generate_video(request: VideoGenerationRequest):
    """
    Generate video using Veo3.
    
    ⚠️ Currently using STUB implementation!
    """
    try:
        logger.info(f"Video generation request: prompt='{request.prompt[:50]}...', duration={request.duration}s")
        
        result = await veo3_stub.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            width=request.width,
            height=request.height,
            fps=request.fps
        )
        
        logger.info(f"Video generation successful: {result['video_url']}")
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )
