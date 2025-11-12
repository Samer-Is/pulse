"""Image generation routes."""

import uuid
import os
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..models.usage import UsageEvent
from ..models.job import Job, JobType, JobStatus
from ..auth.dependencies import require_auth
from ..providers.google_imagen_provider import GoogleImagenProvider
from ..providers.image_types import ImageRequest, GeneratedImage
from ..schemas.image import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImageInfo,
    ImageModelsResponse,
)
from ..utils.s3 import get_s3_manager

router = APIRouter()


def get_image_provider(provider: str) -> GoogleImagenProvider:
    """
    Get image generation provider.
    
    Args:
        provider: Provider name
        
    Returns:
        Image provider instance
        
    Raises:
        HTTPException: If provider not supported or not configured
    """
    if provider == "google":
        sa_json = os.getenv("GCP_VERTEX_SA_JSON")
        project_id = os.getenv("GCP_VERTEX_PROJECT_ID")
        location = os.getenv("GCP_VERTEX_LOCATION", "us-central1")
        
        if not sa_json or not project_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Vertex AI not configured",
            )
        
        return GoogleImagenProvider(
            service_account_json=sa_json,
            project_id=project_id,
            location=location,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )


async def check_image_quota(user: User, count: int, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining image generation quota.
    
    Args:
        user: Current user
        count: Number of images to generate
        db: Database session
        
    Returns:
        User's subscription
        
    Raises:
        HTTPException: If quota exceeded
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    # Check if subscription is active
    if subscription.period_end < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription expired",
        )
    
    # For now, just return subscription
    # Full quota checking will be implemented in Phase 8
    return subscription


async def record_image_usage(
    user_id: str,
    job_id: str,
    provider: str,
    model: str,
    image_count: int,
    db: AsyncSession,
):
    """
    Record usage event for image generation.
    
    Args:
        user_id: User ID
        job_id: Job ID
        provider: Provider name
        model: Model name
        image_count: Number of images generated
        db: Database session
    """
    usage_event = UsageEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        job_id=job_id,
        event_type="image_generation",
        tokens=0,  # Images don't use tokens
        event_metadata={
            "provider": provider,
            "model": model,
            "image_count": image_count,
        },
    )
    
    db.add(usage_event)
    
    # Update subscription image count
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    if subscription:
        subscription.images_generated += image_count
    
    await db.commit()


@router.get("/models", response_model=ImageModelsResponse)
async def list_image_models():
    """
    List available image generation models.
    
    Returns:
        List of available models
    """
    models = [
        {
            "id": "imagegeneration@006",
            "name": "Vertex AI Imagen",
            "provider": "google",
            "description": "Google's latest text-to-image model",
        },
    ]
    
    return ImageModelsResponse(models=models)


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_images(
    request: ImageGenerationRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ImageGenerationResponse:
    """
    Generate images from text prompt.
    
    Args:
        request: Image generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Generated images with URLs
    """
    # Check quota
    await check_image_quota(current_user, request.count, db)
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.IMAGE,
        prompt=request.prompt,
        parameters=request.model_dump(),
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    
    try:
        # Get provider
        provider = get_image_provider(request.provider)
        
        # Convert to provider request
        image_request = ImageRequest(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            count=request.count,
            size=request.size,
            seed=request.seed,
            guidance_scale=request.guidance_scale,
        )
        
        # Generate images
        image_bytes_list = await provider.generate_images(image_request)
        
        if not image_bytes_list:
            raise Exception("No images generated")
        
        # Upload to S3
        s3_manager = get_s3_manager()
        generated_images: List[GeneratedImageInfo] = []
        
        for i, image_bytes in enumerate(image_bytes_list):
            s3_key, presigned_url = s3_manager.upload_image(
                image_bytes=image_bytes,
                user_id=current_user.id,
                job_id=job.id,
                image_index=i,
                extension="png",
            )
            
            generated_images.append(
                GeneratedImageInfo(
                    url=presigned_url,
                    s3_key=s3_key,
                    size=request.size.value,
                    seed=request.seed + i if request.seed else None,
                )
            )
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_url = generated_images[0].url if generated_images else None
        job.model_name = provider.get_model_name()
        await db.commit()
        
        # Record usage
        await record_image_usage(
            user_id=current_user.id,
            job_id=job.id,
            provider=request.provider,
            model=provider.get_model_name(),
            image_count=len(generated_images),
            db=db,
        )
        
        return ImageGenerationResponse(
            job_id=job.id,
            images=generated_images,
            provider=request.provider,
            model=provider.get_model_name(),
            prompt=request.prompt,
            count=len(generated_images),
        )
    
    except Exception as e:
        # Update job status
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}",
        )

