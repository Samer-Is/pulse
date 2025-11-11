"""File schemas."""

from pydantic import BaseModel
from typing import Optional


class PresignedUrlRequest(BaseModel):
    """Request schema for presigned URL."""
    filename: str
    content_type: str


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned URL."""
    upload_url: str
    download_url: str
    file_id: str
    expires_in: int


class FileMetadata(BaseModel):
    """File metadata schema."""
    id: str
    filename: str
    content_type: str
    status: str
    created_at: str

