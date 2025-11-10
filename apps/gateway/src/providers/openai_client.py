"""
OpenAI provider client.
"""

from typing import List, Dict, Any
import openai
from openai import AsyncOpenAI

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIClient:
    """OpenAI API client wrapper."""
    
    @staticmethod
    async def chat_completion(
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenAI.
        
        Args:
            model: Model name (gpt-4o, gpt-4-turbo, gpt-5, etc.)
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Dict with response and usage information
        """
        try:
            logger.info(f"OpenAI chat completion request: model={model}, messages={len(messages)}")
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Return stream object for async iteration
                return {"stream": response}
            
            # Parse response
            choice = response.choices[0]
            usage = response.usage
            
            result = {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
            
            logger.info(f"OpenAI response: tokens={usage.total_tokens}, finish_reason={choice.finish_reason}")
            
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise Exception("OpenAI rate limit exceeded")
        except Exception as e:
            logger.error(f"OpenAI request failed: {str(e)}")
            raise


async def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for chat completion."""
    return await OpenAIClient.chat_completion(model, messages, **kwargs)
