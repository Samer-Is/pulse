"""Video generation routes."""

import uuid
from datetime import datetime
from typing import AsyncIterator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..models.job import Job, JobType, JobStatus
from ..auth.dependencies import require_auth
from ..schemas.video import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoJobStatus,
)
from ..utils.sqs import get_sqs_manager

router = APIRouter()


async def check_video_quota(
    user: User, duration: int, db: AsyncSession
) -> Subscription:
    """
    Check if user has remaining video generation quota.
    
    Args:
        user: Current user
        duration: Video duration in seconds
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


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> VideoGenerationResponse:
    """
    Generate video from text prompt (async via SQS).
    
    Args:
        request: Video generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Job information for polling
    """
    # Check quota
    await check_video_quota(current_user, request.duration, db)
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.VIDEO,
        prompt=request.prompt,
        parameters={
            "provider": request.provider.value,
            "duration": request.duration,
            "style": request.style,
            "aspect_ratio": request.aspect_ratio,
        },
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.commit()
    
    try:
        # Enqueue job to SQS
        sqs_manager = get_sqs_manager()
        message_id = sqs_manager.enqueue_video_job(
            job_id=job.id,
            user_id=current_user.id,
            prompt=request.prompt,
            provider=request.provider.value,
            duration=request.duration,
            style=request.style,
            parameters={
                "aspect_ratio": request.aspect_ratio,
            },
        )
        
        return VideoGenerationResponse(
            job_id=job.id,
            status="pending",
            message="Video generation job queued successfully",
            estimated_time=request.duration * 10,  # Rough estimate: 10x duration
        )
    
    except Exception as e:
        # Update job status
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue video generation: {str(e)}",
        )


@router.get("/{job_id}/status", response_model=VideoJobStatus)
async def get_video_status(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> VideoJobStatus:
    """
    Get video generation job status.
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Job status
    """
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Calculate progress (simple estimation)
    progress = None
    if job.status == JobStatus.PROCESSING:
        progress = 50  # Mid-way through
    elif job.status == JobStatus.COMPLETED:
        progress = 100
    
    return VideoJobStatus(
        job_id=job.id,
        status=job.status.value,
        progress=progress,
        video_url=job.result_url,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )


async def generate_status_stream(
    job_id: str,
    user_id: str,
    db: AsyncSession,
) -> AsyncIterator[str]:
    """
    Generate Server-Sent Events stream for job status updates.
    
    Args:
        job_id: Job ID
        user_id: User ID
        db: Database session
        
    Yields:
        SSE formatted status updates
    """
    max_attempts = 120  # 10 minutes max (5s intervals)
    attempt = 0
    
    while attempt < max_attempts:
        # Fetch job status
        result = await db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            yield f"data: {{\"error\": \"Job not found\"}}\n\n"
            break
        
        # Calculate progress
        progress = 0
        if job.status == JobStatus.PROCESSING:
            progress = min(90, 10 + (attempt * 2))  # Progressive increase
        elif job.status == JobStatus.COMPLETED:
            progress = 100
        
        # Send status update
        status_data = {
            "job_id": job.id,
            "status": job.status.value,
            "progress": progress,
            "video_url": job.result_url,
            "error_message": job.error_message,
        }
        
        yield f"data: {VideoJobStatus(**status_data, created_at=job.created_at.isoformat(), updated_at=job.updated_at.isoformat()).model_dump_json()}\n\n"
        
        # Check if job is complete
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            yield "data: [DONE]\n\n"
            break
        
        # Wait before next poll
        await asyncio.sleep(5)
        attempt += 1
        
        # Refresh DB session
        await db.refresh(job)
    
    if attempt >= max_attempts:
        yield f"data: {{\"error\": \"Timeout waiting for job completion\"}}\n\n"


@router.get("/{job_id}/stream")
async def stream_video_status(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream video generation job status updates via SSE.
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Streaming response
    """
    # Verify job exists and belongs to user
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return StreamingResponse(
        generate_status_stream(job_id, current_user.id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

