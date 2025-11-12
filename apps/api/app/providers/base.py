"""Base provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from enum import Enum

from .types import ChatRequest, ChatResponse, ChatChunk, UsageStats


class ProviderType(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str):
        """
        Initialize provider with API key.
        
        Args:
            api_key: Provider API key
        """
        self.api_key = api_key

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Get chat completion from provider.
        
        Args:
            request: Chat request
            
        Returns:
            Chat response with tokens
        """
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chat completion from provider.
        
        Args:
            request: Chat request
            
        Yields:
            Chat chunks
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens
            model: Optional model name for accurate counting
            
        Returns:
            Token count
        """
        pass

    def _format_messages(self, request: ChatRequest) -> list:
        """
        Format messages for provider-specific format.
        
        Args:
            request: Chat request
            
        Returns:
            Formatted messages
        """
        messages = []
        
        # Add system message if provided
        if request.system:
            messages.append({"role": "system", "content": request.system})
        
        # Add conversation messages
        for msg in request.messages:
            messages.append({"role": msg.role.value, "content": msg.content})
        
        return messages

