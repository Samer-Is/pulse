"""Google Vertex AI Imagen provider for image generation."""

import json
import base64
from typing import List
import httpx
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from .image_base import BaseImageProvider
from .image_types import ImageRequest


class GoogleImagenProvider(BaseImageProvider):
    """Google Vertex AI Imagen image generation provider."""

    def __init__(
        self,
        service_account_json: str,
        project_id: str,
        location: str = "us-central1",
    ):
        """
        Initialize Google Imagen provider.
        
        Args:
            service_account_json: Base64-encoded service account JSON or JSON string
            project_id: GCP project ID
            location: GCP location (default: us-central1)
        """
        super().__init__({"service_account_json": service_account_json})
        self.project_id = project_id
        self.location = location
        
        # Decode service account if base64 encoded
        try:
            sa_json = base64.b64decode(service_account_json).decode("utf-8")
        except Exception:
            sa_json = service_account_json
        
        # Load credentials
        self.credentials = service_account.Credentials.from_service_account_info(
            json.loads(sa_json),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "google"

    def get_model_name(self) -> str:
        """Get model name."""
        return "imagegeneration@006"  # Latest Imagen model as of 2025

    def _get_access_token(self) -> str:
        """Get OAuth access token for Vertex AI."""
        self.credentials.refresh(Request())
        return self.credentials.token

    def _get_endpoint_url(self) -> str:
        """Get Vertex AI Imagen endpoint URL."""
        return (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.location}/"
            f"publishers/google/models/{self.get_model_name()}:predict"
        )

    def _parse_size(self, size_str: str) -> dict:
        """Parse size string to width/height dict."""
        width, height = map(int, size_str.split("x"))
        return {"width": width, "height": height}

    async def generate_images(self, request: ImageRequest) -> List[bytes]:
        """
        Generate images using Vertex AI Imagen.
        
        Args:
            request: Image generation request
            
        Returns:
            List of image bytes
        """
        url = self._get_endpoint_url()
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        
        size = self._parse_size(request.size.value)
        
        # Prepare instances (one per image)
        instances = []
        for i in range(request.count):
            instance = {
                "prompt": request.prompt,
            }
            if request.negative_prompt:
                instance["negativePrompt"] = request.negative_prompt
            if request.seed is not None:
                instance["seed"] = request.seed + i  # Different seed per image
            instances.append(instance)
        
        # Prepare parameters
        parameters = {
            "sampleCount": 1,  # One sample per instance
            "aspectRatio": "1:1" if "x" in request.size.value and request.size.value.split("x")[0] == request.size.value.split("x")[1] else "custom",
            "sampleImageSize": str(max(size["width"], size["height"])),
        }
        
        if request.guidance_scale:
            parameters["guidanceScale"] = request.guidance_scale
        
        payload = {
            "instances": instances,
            "parameters": parameters,
        }
        
        # Make request
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        
        # Extract images from response
        images = []
        if "predictions" in data:
            for prediction in data["predictions"]:
                # Imagen returns base64-encoded images
                if "bytesBase64Encoded" in prediction:
                    image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
                    images.append(image_bytes)
        
        return images

