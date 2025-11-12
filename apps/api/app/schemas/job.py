"""Job schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ..models.job import JobType, JobStatus


class JobCreate(BaseModel):
    """Schema for creating a job."""

    type: JobType
    prompt: Optional[str] = None
    parameters: Optional[dict] = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    status: Optional[JobStatus] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None


class JobResponse(BaseModel):
    """Schema for job response."""

    id: str
    user_id: str
    type: JobType
    status: JobStatus
    prompt: Optional[str] = None
    parameters: Optional[dict] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

