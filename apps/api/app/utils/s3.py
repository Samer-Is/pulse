"""S3 utilities for file storage."""

import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError


class S3Manager:
    """Manage S3 operations for file uploads and presigned URLs."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize S3 manager.
        
        Args:
            bucket_name: S3 bucket name (defaults to env S3_BUCKET_NAME)
            region: AWS region (defaults to env AWS_REGION)
            endpoint_url: Custom endpoint URL for LocalStack (defaults to env AWS_ENDPOINT_URL)
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "pulse-dev-exports")
        self.region = region or os.getenv("AWS_REGION", "eu-central-1")
        endpoint = endpoint_url or os.getenv("AWS_ENDPOINT_URL")
        
        # Create S3 client
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            endpoint_url=endpoint if endpoint else None,
        )

    def upload_file(
        self,
        file_bytes: bytes,
        key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Upload file bytes to S3.
        
        Args:
            file_bytes: File content as bytes
            key: S3 object key (path)
            content_type: MIME type of the file
            metadata: Optional metadata dict
            
        Returns:
            S3 key of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            extra_args = {
                "ContentType": content_type,
            }
            
            if metadata:
                extra_args["Metadata"] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_bytes,
                **extra_args,
            )
            
            return key
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")

    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
    ) -> str:
        """
        Generate presigned URL for S3 object.
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def delete_file(self, key: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError as e:
            print(f"Failed to delete from S3: {str(e)}")
            return False

    def upload_image(
        self,
        image_bytes: bytes,
        user_id: str,
        job_id: str,
        image_index: int = 0,
        extension: str = "png",
    ) -> tuple[str, str]:
        """
        Upload generated image to S3 with organized path.
        
        Args:
            image_bytes: Image content as bytes
            user_id: User ID
            job_id: Job ID
            image_index: Index of image in generation batch
            extension: File extension (default: png)
            
        Returns:
            Tuple of (s3_key, presigned_url)
        """
        # Generate organized S3 key
        key = f"images/{user_id}/{job_id}/{image_index}.{extension}"
        
        # Upload with proper content type
        self.upload_file(
            file_bytes=image_bytes,
            key=key,
            content_type=f"image/{extension}",
            metadata={
                "user_id": user_id,
                "job_id": job_id,
                "index": str(image_index),
            },
        )
        
        # Generate presigned URL (valid for 24 hours for images)
        url = self.generate_presigned_url(key, expiration=86400)
        
        return key, url


# Singleton instance
_s3_manager: Optional[S3Manager] = None


def get_s3_manager() -> S3Manager:
    """
    Get or create S3Manager singleton instance.
    
    Returns:
        S3Manager instance
    """
    global _s3_manager
    if _s3_manager is None:
        _s3_manager = S3Manager()
    return _s3_manager

