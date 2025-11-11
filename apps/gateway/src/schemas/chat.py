"""Chat request/response schemas."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # user, assistant, system
    content: str


class ChatCompletionRequest(BaseModel):
    """Chat completion request schema."""
    model: str  # openai:gpt-4o, anthropic:claude-4.5, google:gemini-1.5
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2000
    system: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None


class ChatCompletionChoice(BaseModel):
    """Single completion choice."""
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Chat completion response schema."""
    id: str
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

