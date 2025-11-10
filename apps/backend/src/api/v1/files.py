"""
Files routes - S3 file uploads with presigned URLs.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import boto3
from datetime import timedelta
import uuid

from ...core import get_db, get_logger, get_current_user
from ...core.config import get_settings
from ...models import User, File as FileModel

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()

s3_client = boto3.client('s3', region_name=settings.AWS_REGION)


# Schemas
class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str


class PresignedUrlResponse(BaseModel):
    upload_url: str
    download_url: str
    file_id: str
    expires_in: int


@router.post("/presigned-upload", response_model=PresignedUrlResponse)
async def get_presigned_upload_url(
    request: PresignedUrlRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Generate presigned URL for file upload to S3.
    
    Args:
        filename: Original filename
        content_type: MIME type
    
    Returns:
        upload_url: Presigned URL for PUT request
        download_url: URL for downloading after upload
        file_id: Unique file ID
        expires_in: URL expiration in seconds
    """
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_key = f"users/{user.id}/{file_id}/{request.filename}"
    
    try:
        # Generate presigned URL for upload (PUT)
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_ASSETS,
                'Key': file_key,
                'ContentType': request.content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        # Generate presigned URL for download (GET)
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_ASSETS,
                'Key': file_key
            },
            ExpiresIn=86400  # 24 hours
        )
        
        # Create file record
        file_record = FileModel(
            user_id=user.id,
            filename=request.filename,
            file_key=file_key,
            content_type=request.content_type,
            status="pending"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        logger.info(f"Presigned URL generated: user={user.id}, file={file_id}")
        
        return {
            "data": {
                "upload_url": upload_url,
                "download_url": download_url,
                "file_id": str(file_record.id),
                "expires_in": 3600
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )


@router.get("/list")
async def list_files(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List user's uploaded files."""
    
    files = db.query(FileModel).filter(
        FileModel.user_id == user.id
    ).order_by(FileModel.created_at.desc()).limit(50).all()
    
    return {
        "data": {
            "files": [
                {
                    "id": str(f.id),
                    "filename": f.filename,
                    "content_type": f.content_type,
                    "status": f.status,
                    "created_at": f.created_at.isoformat()
                }
                for f in files
            ]
        }
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a file from S3 and database."""
    
    file_record = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == user.id
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete from S3
    try:
        s3_client.delete_object(
            Bucket=settings.S3_ASSETS,
            Key=file_record.file_key
        )
    except Exception as e:
        logger.error(f"Failed to delete from S3: {str(e)}")
    
    # Delete from database
    db.delete(file_record)
    db.commit()
    
    logger.info(f"File deleted: file={file_id}, user={user.id}")
    
    return {
        "data": {
            "message": "File deleted successfully"
        }
    }
