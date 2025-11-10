"""
Google (Gemini) provider client.
"""

from typing import List, Dict, Any
import google.generativeai as genai

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Configure Google API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class GoogleClient:
    """Google Gemini API client wrapper."""
    
    @staticmethod
    async def chat_completion(
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Google Gemini.
        
        Args:
            model: Model name (gemini-1.5-pro, gemini-pro, etc.)
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with response and usage information
        """
        try:
            logger.info(f"Google chat completion request: model={model}, messages={len(messages)}")
            
            # Initialize model
            gemini_model = genai.GenerativeModel(model)
            
            # Convert messages to Gemini format
            # Gemini uses "parts" format
            prompt = "\n\n".join([
                f"{msg['role']}: {msg['content']}" for msg in messages
            ])
            
            # Generate content
            response = await gemini_model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            # Parse response
            result = {
                "id": f"gemini-{hash(response.text)}",
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response.text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                }
            }
            
            logger.info(f"Google response: tokens={result['usage']['total_tokens']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Google request failed: {str(e)}")
            raise


async def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for chat completion."""
    return await GoogleClient.chat_completion(model, messages, **kwargs)
