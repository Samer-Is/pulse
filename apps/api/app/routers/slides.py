"""Slide generation routes."""

import uuid
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..models.usage import UsageEvent
from ..models.job import Job, JobType, JobStatus
from ..auth.dependencies import require_auth
from ..schemas.slides import (
    SlideGenerationRequest,
    SlideGenerationResponse,
    OutlineGenerationRequest,
    OutlineGenerationResponse,
    SlideContent,
)
from ..services.slide_generator import SlideGenerator
from ..providers import get_provider, ProviderType
from ..providers.types import ChatRequest, ChatMessage, ChatRole
from ..utils.s3 import get_s3_manager

router = APIRouter()


async def check_slide_quota(user: User, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining slide export quota.
    
    Args:
        user: Current user
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
    
    return subscription


async def generate_outline_with_ai(
    topic: str,
    num_slides: int,
    audience: str = None,
    style: str = None,
) -> list[SlideContent]:
    """
    Generate presentation outline using AI.
    
    Args:
        topic: Presentation topic
        num_slides: Number of slides to generate
        audience: Target audience
        style: Presentation style
        
    Returns:
        List of slide contents
    """
    # Build prompt for AI
    prompt = f"""Create a presentation outline for the following topic: "{topic}"

Requirements:
- Generate exactly {num_slides} slides (excluding title slide)
- Each slide should have a clear title and 3-5 bullet points
- Make it engaging and informative
"""
    
    if audience:
        prompt += f"- Target audience: {audience}\n"
    
    if style:
        prompt += f"- Presentation style: {style}\n"
    
    prompt += """
Format your response as JSON with this structure:
{
  "slides": [
    {
      "title": "Slide Title",
      "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"]
    }
  ]
}

Respond ONLY with valid JSON, no additional text."""
    
    # Use OpenAI for outline generation (or fallback to Anthropic)
    try:
        provider = get_provider(ProviderType.OPENAI)
        model = "gpt-3.5-turbo"
    except:
        provider = get_provider(ProviderType.ANTHROPIC)
        model = "claude-3-haiku-20240307"
    
    # Get AI response
    chat_request = ChatRequest(
        messages=[ChatMessage(role=ChatRole.USER, content=prompt)],
        model=model,
        temperature=0.7,
        max_tokens=2000,
        stream=False,
    )
    
    response = await provider.chat_completion(chat_request)
    
    # Parse JSON response
    try:
        # Extract JSON from response (might have markdown code blocks)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        data = json.loads(content)
        slides = [SlideContent(**slide) for slide in data["slides"]]
        return slides[:num_slides]  # Ensure we don't exceed requested number
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}",
        )


@router.post("/generate-outline", response_model=OutlineGenerationResponse)
async def generate_outline(
    request: OutlineGenerationRequest,
    current_user: User = Depends(require_auth),
) -> OutlineGenerationResponse:
    """
    Generate presentation outline using AI.
    
    Args:
        request: Outline generation request
        current_user: Current authenticated user
        
    Returns:
        Generated outline
    """
    slides = await generate_outline_with_ai(
        topic=request.topic,
        num_slides=request.num_slides,
        audience=request.audience,
        style=request.style,
    )
    
    return OutlineGenerationResponse(
        topic=request.topic,
        slides=slides,
    )


@router.post("/generate", response_model=SlideGenerationResponse)
async def generate_slides(
    slide_request: SlideGenerationRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> SlideGenerationResponse:
    """
    Generate presentation slides in PPTX or PDF format.
    
    Args:
        slide_request: Slide generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Download URL and metadata
    """
    # Check quota
    await check_slide_quota(current_user, db)
    
    # Validate format
    if slide_request.format not in ["pptx", "pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'pptx' or 'pdf'",
        )
    
    # Determine slides to use
    slides = []
    title = ""
    
    if slide_request.auto_generate and slide_request.topic:
        # Generate slides with AI
        title = slide_request.topic
        slides = await generate_outline_with_ai(
            topic=slide_request.topic,
            num_slides=slide_request.num_slides or 5,
        )
    elif slide_request.outline:
        # Use manual outline
        title = slide_request.topic or "Presentation"
        slides = slide_request.outline
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either provide 'topic' with 'auto_generate=true' or provide 'outline'",
        )
    
    if not slides:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No slides to generate",
        )
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.SLIDES,
        prompt=f"Slides: {title}",
        parameters={"format": slide_request.format, "slide_count": len(slides)},
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    
    try:
        # Generate slides
        slide_generator = SlideGenerator()
        
        if slide_request.format == "pptx":
            slide_bytes = await slide_generator.generate_pptx(title, slides, slide_request.template)
            content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            extension = "pptx"
        else:  # pdf
            slide_bytes = await slide_generator.generate_pdf(title, slides)
            content_type = "application/pdf"
            extension = "pdf"
        
        # Upload to S3
        s3_manager = get_s3_manager()
        s3_key = f"slides/{current_user.id}/{job.id}/presentation.{extension}"
        
        s3_manager.upload_file(
            file_bytes=slide_bytes,
            key=s3_key,
            content_type=content_type,
            metadata={
                "user_id": current_user.id,
                "job_id": job.id,
                "title": title,
                "slide_count": str(len(slides)),
            },
        )
        
        # Generate presigned URL (valid for 7 days)
        download_url = s3_manager.generate_presigned_url(s3_key, expiration=604800)
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_url = download_url
        await db.commit()
        
        # Record usage
        usage_event = UsageEvent(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            job_id=job.id,
            event_type="slides_export",
            tokens=0,
            event_metadata={
                "format": slide_request.format,
                "slide_count": len(slides),
            },
        )
        db.add(usage_event)
        
        # Update subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.slides_generated += 1
        
        await db.commit()
        
        # Calculate expiration
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        return SlideGenerationResponse(
            job_id=job.id,
            format=slide_request.format,
            download_url=download_url,
            s3_key=s3_key,
            slide_count=len(slides),
            expires_at=expires_at,
        )
    
    except Exception as e:
        # Update job status
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Slide generation failed: {str(e)}",
        )

