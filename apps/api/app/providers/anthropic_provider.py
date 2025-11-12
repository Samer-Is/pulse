"""Anthropic provider implementation."""

from typing import AsyncIterator, Optional
from anthropic import AsyncAnthropic

from .base import BaseProvider
from .types import ChatRequest, ChatResponse, ChatChunk


class AnthropicProvider(BaseProvider):
    """Anthropic (Claude) chat completion provider."""

    def __init__(self, api_key: str):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Get chat completion from Anthropic.
        
        Args:
            request: Chat request
            
        Returns:
            Chat response
        """
        # Anthropic uses separate system parameter
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.messages
            if msg.role.value != "system"
        ]
        
        response = await self.client.messages.create(
            model=request.model,
            messages=messages,
            system=request.system or "",
            temperature=request.temperature,
            max_tokens=request.max_tokens or 2048,
            stream=False,
        )
        
        content = response.content[0].text if response.content else ""
        
        return ChatResponse(
            content=content,
            model=response.model,
            provider=self.provider_name,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
        )

    async def chat_completion_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chat completion from Anthropic.
        
        Args:
            request: Chat request
            
        Yields:
            Chat chunks
        """
        # Anthropic uses separate system parameter
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.messages
            if msg.role.value != "system"
        ]
        
        async with self.client.messages.stream(
            model=request.model,
            messages=messages,
            system=request.system or "",
            temperature=request.temperature,
            max_tokens=request.max_tokens or 2048,
        ) as stream:
            async for text in stream.text_stream:
                yield ChatChunk(content=text)

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens (approximate for Anthropic).
        
        Anthropic uses a different tokenizer, but we approximate with
        the rule of thumb: 1 token ≈ 4 characters.
        
        Args:
            text: Text to count
            model: Model name (unused)
            
        Returns:
            Approximate token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English
        return len(text) // 4

