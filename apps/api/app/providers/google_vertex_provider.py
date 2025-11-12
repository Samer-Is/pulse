"""Google Vertex AI provider implementation."""

import json
import base64
from typing import AsyncIterator, Optional
import httpx
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from .base import BaseProvider
from .types import ChatRequest, ChatResponse, ChatChunk


class GoogleVertexProvider(BaseProvider):
    """Google Vertex AI (Gemini) chat completion provider."""

    def __init__(
        self,
        service_account_json: str,
        project_id: str,
        location: str = "us-central1",
    ):
        """
        Initialize Google Vertex AI provider.
        
        Args:
            service_account_json: Base64-encoded service account JSON or JSON string
            project_id: GCP project ID
            location: GCP location (default: us-central1)
        """
        super().__init__(service_account_json)
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

    def _get_access_token(self) -> str:
        """Get OAuth access token for Vertex AI."""
        self.credentials.refresh(Request())
        return self.credentials.token

    def _get_endpoint_url(self, model: str, stream: bool = False) -> str:
        """Get Vertex AI endpoint URL."""
        action = "streamGenerateContent" if stream else "generateContent"
        return (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.location}/"
            f"publishers/google/models/{model}:{action}"
        )

    def _format_for_vertex(self, request: ChatRequest) -> dict:
        """Format request for Vertex AI Gemini API."""
        contents = []
        system_instruction = None
        
        # Handle system message
        if request.system:
            system_instruction = {"parts": [{"text": request.system}]}
        
        # Format conversation messages
        for msg in request.messages:
            role = "user" if msg.role.value in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 2048,
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        return payload

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Get chat completion from Vertex AI.
        
        Args:
            request: Chat request
            
        Returns:
            Chat response
        """
        url = self._get_endpoint_url(request.model, stream=False)
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        payload = self._format_for_vertex(request)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        
        # Extract content and usage
        content = ""
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                content = "".join(
                    part.get("text", "") for part in candidate["content"]["parts"]
                )
        
        # Get usage metadata
        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        completion_tokens = usage.get("candidatesTokenCount", 0)
        
        return ChatResponse(
            content=content,
            model=request.model,
            provider=self.provider_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    async def chat_completion_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chat completion from Vertex AI.
        
        Args:
            request: Chat request
            
        Yields:
            Chat chunks
        """
        url = self._get_endpoint_url(request.model, stream=True)
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        payload = self._format_for_vertex(request)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    # Vertex AI streams JSON objects, one per line
                    try:
                        data = json.loads(line)
                        
                        if "candidates" in data and len(data["candidates"]) > 0:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        yield ChatChunk(content=part["text"])
                    except json.JSONDecodeError:
                        continue

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens (approximate for Gemini).
        
        Similar to Anthropic, we use an approximation.
        
        Args:
            text: Text to count
            model: Model name (unused)
            
        Returns:
            Approximate token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4

