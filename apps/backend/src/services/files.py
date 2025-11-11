"""File service for S3 operations."""

import boto3
from botocore.exceptions import ClientError
from typing import Optional

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

s3_client = boto3.client('s3', region_name=settings.AWS_REGION)


def generate_presigned_upload_url(
    bucket: str,
    key: str,
    content_type: str,
    expires_in: int = 3600
) -> str:
    """
    Generate presigned URL for uploading to S3.
    
    Args:
        bucket: S3 bucket name
        key: Object key
        content_type: MIME type
        expires_in: URL expiration in seconds
    
    Returns:
        Presigned upload URL
    """
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned upload URL: {str(e)}")
        raise


def generate_presigned_download_url(
    bucket: str,
    key: str,
    expires_in: int = 86400
) -> str:
    """
    Generate presigned URL for downloading from S3.
    
    Args:
        bucket: S3 bucket name
        key: Object key
        expires_in: URL expiration in seconds
    
    Returns:
        Presigned download URL
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned download URL: {str(e)}")
        raise


def delete_file(bucket: str, key: str) -> bool:
    """
    Delete file from S3.
    
    Args:
        bucket: S3 bucket name
        key: Object key
    
    Returns:
        True if deleted successfully
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"File deleted from S3: bucket={bucket}, key={key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {str(e)}")
        return False

