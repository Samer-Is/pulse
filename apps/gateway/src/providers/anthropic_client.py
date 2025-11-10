"""
Anthropic (Claude) provider client.
"""

from typing import List, Dict, Any
import anthropic
from anthropic import AsyncAnthropic

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize Anthropic client
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


class AnthropicClient:
    """Anthropic Claude API client wrapper."""
    
    @staticmethod
    async def chat_completion(
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system: str = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Anthropic Claude.
        
        Args:
            model: Model name (claude-4.5-sonnet, etc.)
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System message (optional)
        
        Returns:
            Dict with response and usage information
        """
        try:
            logger.info(f"Anthropic chat completion request: model={model}, messages={len(messages)}")
            
            # Extract system message if present
            if not system and messages and messages[0].get("role") == "system":
                system = messages[0]["content"]
                messages = messages[1:]
            
            response = await client.messages.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                system=system if system else anthropic.NOT_GIVEN
            )
            
            # Parse response
            content = response.content[0]
            usage = response.usage
            
            result = {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content.text
                        },
                        "finish_reason": response.stop_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens
                }
            }
            
            logger.info(f"Anthropic response: tokens={result['usage']['total_tokens']}, finish_reason={response.stop_reason}")
            
            return result
            
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise Exception(f"Anthropic API error: {str(e)}")
        except Exception as e:
            logger.error(f"Anthropic request failed: {str(e)}")
            raise


async def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for chat completion."""
    return await AnthropicClient.chat_completion(model, messages, **kwargs)
