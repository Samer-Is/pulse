"""Common types for AI providers."""

from typing import Optional, List, Dict, Any, AsyncIterator
from pydantic import BaseModel
from enum import Enum


class ProviderType(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ChatRole(str, Enum):
    """Chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Chat message structure."""

    role: ChatRole
    content: str


class ChatRequest(BaseModel):
    """Chat completion request."""

    messages: List[ChatMessage]
    model: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: bool = True
    system: Optional[str] = None


class ChatChunk(BaseModel):
    """Streaming chat response chunk."""

    content: str
    finish_reason: Optional[str] = None


class ChatResponse(BaseModel):
    """Complete chat response."""

    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: Optional[str] = None


class UsageStats(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

