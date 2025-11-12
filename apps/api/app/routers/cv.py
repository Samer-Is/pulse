"""CV generation routes."""

import uuid
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
from ..schemas.cv import CVRequest, CVResponse
from ..services.cv_generator import CVGenerator
from ..utils.s3 import get_s3_manager

router = APIRouter()


async def check_cv_quota(user: User, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining CV export quota.
    
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
    
    # For now, just return subscription
    # Full quota checking will be implemented in Phase 8
    return subscription


async def record_cv_usage(
    user_id: str,
    job_id: str,
    format: str,
    db: AsyncSession,
):
    """
    Record usage event for CV generation.
    
    Args:
        user_id: User ID
        job_id: Job ID
        format: Export format (docx or pdf)
        db: Database session
    """
    usage_event = UsageEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        job_id=job_id,
        event_type="cv_export",
        tokens=0,  # CVs don't use tokens
        event_metadata={
            "format": format,
        },
    )
    
    db.add(usage_event)
    
    # Update subscription CV count
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    if subscription:
        subscription.cvs_generated += 1
    
    await db.commit()


@router.post("/generate", response_model=CVResponse)
async def generate_cv(
    cv_request: CVRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> CVResponse:
    """
    Generate CV in DOCX or PDF format.
    
    Args:
        cv_request: CV data and format
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Download URL and metadata
    """
    # Check quota
    await check_cv_quota(current_user, db)
    
    # Validate format
    if cv_request.format not in ["docx", "pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'docx' or 'pdf'",
        )
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.CV,
        prompt=f"CV for {cv_request.personal_info.full_name}",
        parameters={"format": cv_request.format},
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    
    try:
        # Generate CV
        cv_generator = CVGenerator()
        
        if cv_request.format == "docx":
            cv_bytes = await cv_generator.generate_docx(cv_request)
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            extension = "docx"
        else:  # pdf
            cv_bytes = await cv_generator.generate_pdf(cv_request)
            content_type = "application/pdf"
            extension = "pdf"
        
        # Upload to S3
        s3_manager = get_s3_manager()
        s3_key = f"cvs/{current_user.id}/{job.id}/cv.{extension}"
        
        s3_manager.upload_file(
            file_bytes=cv_bytes,
            key=s3_key,
            content_type=content_type,
            metadata={
                "user_id": current_user.id,
                "job_id": job.id,
                "name": cv_request.personal_info.full_name,
            },
        )
        
        # Generate presigned URL (valid for 7 days for CVs)
        download_url = s3_manager.generate_presigned_url(s3_key, expiration=604800)
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_url = download_url
        await db.commit()
        
        # Record usage
        await record_cv_usage(
            user_id=current_user.id,
            job_id=job.id,
            format=cv_request.format,
            db=db,
        )
        
        # Calculate expiration
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        return CVResponse(
            job_id=job.id,
            format=cv_request.format,
            download_url=download_url,
            s3_key=s3_key,
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
            detail=f"CV generation failed: {str(e)}",
        )

