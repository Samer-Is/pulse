"""Chat completion schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field

from ..providers.types import ChatMessage


class ChatCompletionRequest(BaseModel):
    """Chat completion request schema."""

    messages: List[ChatMessage]
    provider: str = Field(
        ..., 
        description="Provider: openai, anthropic, or google"
    )
    model: str = Field(
        ...,
        description="Model name (e.g., gpt-4, claude-3-opus-20240229, gemini-pro)"
    )
    temperature: Optional[float] = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        2048,
        ge=1,
        le=8192,
        description="Maximum tokens to generate"
    )
    system: Optional[str] = Field(
        None,
        description="System message"
    )


class ChatCompletionResponse(BaseModel):
    """Chat completion response schema."""

    job_id: str
    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: Optional[str] = None


class StreamChunkResponse(BaseModel):
    """Streaming chunk response schema."""

    job_id: str
    content: str
    finish_reason: Optional[str] = None


class ModelInfo(BaseModel):
    """Model information schema."""

    id: str
    name: str
    provider: str
    description: Optional[str] = None


class ModelsListResponse(BaseModel):
    """Available models list response."""

    models: List[ModelInfo]

