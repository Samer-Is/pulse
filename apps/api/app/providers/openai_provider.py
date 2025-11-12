"""OpenAI provider implementation."""

from typing import AsyncIterator, Optional
import tiktoken
from openai import AsyncOpenAI

from .base import BaseProvider
from .types import ChatRequest, ChatResponse, ChatChunk


class OpenAIProvider(BaseProvider):
    """OpenAI chat completion provider."""

    def __init__(self, api_key: str):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Get chat completion from OpenAI.
        
        Args:
            request: Chat request
            
        Returns:
            Chat response
        """
        messages = self._format_messages(request)
        
        response = await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        
        choice = response.choices[0]
        usage = response.usage
        
        return ChatResponse(
            content=choice.message.content,
            model=response.model,
            provider=self.provider_name,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            finish_reason=choice.finish_reason,
        )

    async def chat_completion_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chat completion from OpenAI.
        
        Args:
            request: Chat request
            
        Yields:
            Chat chunks
        """
        messages = self._format_messages(request)
        
        stream = await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason
                
                if delta.content:
                    yield ChatChunk(
                        content=delta.content,
                        finish_reason=finish_reason,
                    )

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens using tiktoken.
        
        Args:
            text: Text to count
            model: Model name (defaults to gpt-3.5-turbo)
            
        Returns:
            Token count
        """
        try:
            model = model or "gpt-3.5-turbo"
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to cl100k_base encoding (GPT-4/3.5)
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))

