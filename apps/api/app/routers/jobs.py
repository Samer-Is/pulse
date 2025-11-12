"""Job management routes."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..database import get_db
from ..models.user import User
from ..models.job import Job, JobStatus
from ..schemas.job import JobCreate, JobResponse, JobUpdate
from ..auth.dependencies import require_auth

router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Create a new job.
    
    Args:
        job_data: Job creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created job information
    """
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=job_data.type,
        prompt=job_data.prompt,
        parameters=job_data.parameters,
        status=JobStatus.PENDING,
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # TODO: Queue job for processing via SQS
    
    return JobResponse.model_validate(job)


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[JobStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[JobResponse]:
    """
    List user's jobs with optional filtering.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        status_filter: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List of jobs
    """
    query = select(Job).where(Job.user_id == current_user.id).order_by(desc(Job.created_at))
    
    if status_filter:
        query = query.where(Job.status == status_filter)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Get a specific job by ID.
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Job information
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
    
    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Update a job (primarily for status updates).
    
    Args:
        job_id: Job ID
        job_update: Job update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated job information
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
    
    # Update job fields
    if job_update.status is not None:
        job.status = job_update.status
    if job_update.result_url is not None:
        job.result_url = job_update.result_url
    if job_update.error_message is not None:
        job.error_message = job_update.error_message
    
    await db.commit()
    await db.refresh(job)
    
    return JobResponse.model_validate(job)


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a job.
    
    Args:
        job_id: Job ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Deletion confirmation
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
    
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted successfully"}

