"""SQS utilities for job queue management."""

import os
import json
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError


class SQSManager:
    """Manage SQS operations for job queue."""

    def __init__(
        self,
        queue_url: Optional[str] = None,
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize SQS manager.
        
        Args:
            queue_url: SQS queue URL (defaults to env SQS_QUEUE_URL)
            region: AWS region (defaults to env AWS_REGION)
            endpoint_url: Custom endpoint URL for LocalStack (defaults to env AWS_ENDPOINT_URL)
        """
        self.queue_url = queue_url or os.getenv("SQS_QUEUE_URL")
        self.region = region or os.getenv("AWS_REGION", "eu-central-1")
        endpoint = endpoint_url or os.getenv("AWS_ENDPOINT_URL")
        
        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL must be set")
        
        # Create SQS client
        self.sqs_client = boto3.client(
            "sqs",
            region_name=self.region,
            endpoint_url=endpoint if endpoint else None,
        )

    def send_message(
        self,
        message_body: Dict[str, Any],
        delay_seconds: int = 0,
        message_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send message to SQS queue.
        
        Args:
            message_body: Message payload as dict
            delay_seconds: Delay before message becomes visible (0-900)
            message_attributes: Optional message attributes
            
        Returns:
            Message ID
            
        Raises:
            Exception: If send fails
        """
        try:
            params = {
                "QueueUrl": self.queue_url,
                "MessageBody": json.dumps(message_body),
            }
            
            if delay_seconds > 0:
                params["DelaySeconds"] = delay_seconds
            
            if message_attributes:
                params["MessageAttributes"] = message_attributes
            
            response = self.sqs_client.send_message(**params)
            return response["MessageId"]
        except ClientError as e:
            raise Exception(f"Failed to send SQS message: {str(e)}")

    def receive_messages(
        self,
        max_messages: int = 1,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 300,
    ) -> list:
        """
        Receive messages from SQS queue.
        
        Args:
            max_messages: Maximum number of messages to receive (1-10)
            wait_time_seconds: Long polling wait time (0-20)
            visibility_timeout: Message visibility timeout in seconds
            
        Returns:
            List of messages
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                VisibilityTimeout=visibility_timeout,
                MessageAttributeNames=["All"],
            )
            return response.get("Messages", [])
        except ClientError as e:
            print(f"Failed to receive SQS messages: {str(e)}")
            return []

    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete message from queue.
        
        Args:
            receipt_handle: Message receipt handle
            
        Returns:
            True if successful
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            return True
        except ClientError as e:
            print(f"Failed to delete SQS message: {str(e)}")
            return False

    def enqueue_video_job(
        self,
        job_id: str,
        user_id: str,
        prompt: str,
        provider: str,
        duration: int,
        style: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Enqueue video generation job.
        
        Args:
            job_id: Job ID
            user_id: User ID
            prompt: Video prompt
            provider: Video provider (runway or pika)
            duration: Video duration in seconds
            style: Optional style/preset
            parameters: Optional additional parameters
            
        Returns:
            Message ID
        """
        message = {
            "job_id": job_id,
            "user_id": user_id,
            "job_type": "video",
            "prompt": prompt,
            "provider": provider,
            "duration": duration,
            "style": style,
            "parameters": parameters or {},
        }
        
        return self.send_message(message)


# Singleton instance
_sqs_manager: Optional[SQSManager] = None


def get_sqs_manager() -> SQSManager:
    """
    Get or create SQSManager singleton instance.
    
    Returns:
        SQSManager instance
    """
    global _sqs_manager
    if _sqs_manager is None:
        _sqs_manager = SQSManager()
    return _sqs_manager

