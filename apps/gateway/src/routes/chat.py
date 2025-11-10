"""
Chat routes - Multi-model AI chat completions.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional

from ..core.logging import get_logger
from ..providers import openai_client, anthropic_client

logger = get_logger(__name__)
router = APIRouter()


# Schemas
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False
    system: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    choices: List[Dict]
    usage: Dict


# Model routing logic
def get_provider_client(model: str):
    """Route model to appropriate provider."""
    
    model_lower = model.lower()
    
    if model_lower.startswith("gpt") or model_lower.startswith("openai:"):
        return ("openai", openai_client)
    elif model_lower.startswith("claude") or model_lower.startswith("anthropic:"):
        return ("anthropic", anthropic_client)
    elif model_lower.startswith("gemini") or model_lower.startswith("google:"):
        # TODO: Implement Google client
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google Gemini provider not yet implemented"
        )
    else:
        # Default to OpenAI
        return ("openai", openai_client)


# Routes
@router.post("/complete", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    Multi-model chat completion endpoint.
    
    Supports:
    - OpenAI (GPT-4, GPT-5)
    - Anthropic (Claude 4.5)
    - Google (Gemini Pro) - Coming soon
    
    Model routing is based on model name prefix:
    - gpt-*, openai:* → OpenAI
    - claude*, anthropic:* → Anthropic
    - gemini*, google:* → Google
    """
    try:
        # Route to provider
        provider_name, provider_client = get_provider_client(request.model)
        
        logger.info(f"Chat completion request: model={request.model}, provider={provider_name}, messages={len(request.messages)}")
        
        # Prepare messages
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Add system message if provided and not already in messages
        if request.system and (not messages or messages[0]["role"] != "system"):
            messages.insert(0, {"role": "system", "content": request.system})
        
        # Call provider
        if provider_name == "openai":
            # Strip provider prefix from model name
            model_name = request.model.replace("openai:", "")
            response = await provider_client.chat_completion(
                model=model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
        elif provider_name == "anthropic":
            # Strip provider prefix from model name
            model_name = request.model.replace("anthropic:", "")
            response = await provider_client.chat_completion(
                model=model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system=request.system
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider_name}"
            )
        
        # TODO: Log usage to database
        # TODO: Check rate limits
        # TODO: Check quotas
        
        logger.info(f"Chat completion successful: tokens={response['usage']['total_tokens']}")
        
        return {"data": response}
        
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        
        # Map errors to HTTP status codes
        error_message = str(e)
        
        if "rate limit" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        elif "quota" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Quota exceeded"
            )
        elif "timeout" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Provider request timed out"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat completion failed: {error_message}"
            )


@router.get("/models")
async def list_models():
    """List available chat models."""
    
    models = [
        {
            "id": "gpt-4o",
            "name": "GPT-4 Optimized",
            "provider": "openai",
            "context_window": 128000
        },
        {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "openai",
            "context_window": 128000
        },
        {
            "id": "claude-4.5-sonnet",
            "name": "Claude 4.5 Sonnet",
            "provider": "anthropic",
            "context_window": 200000
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "provider": "google",
            "context_window": 1000000,
            "available": False
        }
    ]
    
    return {"data": {"models": models}}
