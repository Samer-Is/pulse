"""Chat completion routes."""

import uuid
from datetime import datetime
from typing import AsyncIterator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription
from ..models.usage import UsageEvent
from ..models.job import Job, JobType, JobStatus
from ..auth.dependencies import require_auth
from ..providers import get_provider, ProviderType
from ..providers.types import ChatRequest, ChatResponse
from ..schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    StreamChunkResponse,
    ModelsListResponse,
    ModelInfo,
)

router = APIRouter()


@router.get("/models", response_model=ModelsListResponse)
async def list_models():
    """
    List available chat models.
    
    Returns:
        List of available models
    """
    models = [
        # OpenAI models
        ModelInfo(
            id="gpt-4",
            name="GPT-4",
            provider="openai",
            description="Most capable GPT-4 model"
        ),
        ModelInfo(
            id="gpt-4-turbo-preview",
            name="GPT-4 Turbo",
            provider="openai",
            description="Latest GPT-4 Turbo model"
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider="openai",
            description="Fast and cost-effective"
        ),
        # Anthropic models
        ModelInfo(
            id="claude-3-opus-20240229",
            name="Claude 3 Opus",
            provider="anthropic",
            description="Most capable Claude model"
        ),
        ModelInfo(
            id="claude-3-sonnet-20240229",
            name="Claude 3 Sonnet",
            provider="anthropic",
            description="Balanced performance"
        ),
        ModelInfo(
            id="claude-3-haiku-20240307",
            name="Claude 3 Haiku",
            provider="anthropic",
            description="Fastest Claude model"
        ),
        # Google models
        ModelInfo(
            id="gemini-pro",
            name="Gemini Pro",
            provider="google",
            description="Google's most capable model"
        ),
        ModelInfo(
            id="gemini-pro-vision",
            name="Gemini Pro Vision",
            provider="google",
            description="Multimodal model with vision"
        ),
    ]
    
    return ModelsListResponse(models=models)


async def check_quota(user: User, db: AsyncSession) -> Subscription:
    """
    Check if user has remaining chat quota.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        User's subscription
        
    Raises:
        HTTPException: If quota exceeded
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    # Check if subscription is active
    if subscription.period_end < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription expired",
        )
    
    # For now, we'll implement quotas in Phase 8
    # Just return the subscription
    return subscription


async def record_usage(
    user_id: str,
    job_id: str,
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    db: AsyncSession,
):
    """
    Record usage event for chat completion.
    
    Args:
        user_id: User ID
        job_id: Job ID
        provider: Provider name
        model: Model name
        prompt_tokens: Input tokens
        completion_tokens: Output tokens
        db: Database session
    """
    usage_event = UsageEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        job_id=job_id,
        event_type="chat_completion",
        tokens=prompt_tokens + completion_tokens,
        event_metadata={
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    )
    
    db.add(usage_event)
    
    # Update subscription token usage
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()
    if subscription:
        subscription.tokens_used += prompt_tokens + completion_tokens
    
    await db.commit()


@router.post("/complete", response_model=ChatCompletionResponse)
async def chat_complete(
    request: ChatCompletionRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ChatCompletionResponse:
    """
    Get chat completion (non-streaming).
    
    Args:
        request: Chat completion request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat completion response
    """
    # Check quota
    await check_quota(current_user, db)
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.CHAT,
        prompt=request.messages[-1].content if request.messages else "",
        parameters=request.model_dump(exclude={"messages"}),
        model_name=request.model,
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    
    try:
        # Get provider
        provider = get_provider(ProviderType(request.provider))
        
        # Convert to provider request
        chat_request = ChatRequest(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
            system=request.system,
        )
        
        # Get completion
        response = await provider.chat_completion(chat_request)
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.tokens_used = response.total_tokens
        await db.commit()
        
        # Record usage
        await record_usage(
            user_id=current_user.id,
            job_id=job.id,
            provider=response.provider,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            db=db,
        )
        
        return ChatCompletionResponse(
            job_id=job.id,
            content=response.content,
            model=response.model,
            provider=response.provider,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            finish_reason=response.finish_reason,
        )
    
    except Exception as e:
        # Update job status
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}",
        )


async def generate_stream(
    request: ChatCompletionRequest,
    user: User,
    job_id: str,
    db: AsyncSession,
) -> AsyncIterator[str]:
    """
    Generate streaming chat response.
    
    Args:
        request: Chat completion request
        user: Current user
        job_id: Job ID
        db: Database session
        
    Yields:
        Server-Sent Events formatted chunks
    """
    try:
        # Get provider
        provider = get_provider(ProviderType(request.provider))
        
        # Convert to provider request
        chat_request = ChatRequest(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
            system=request.system,
        )
        
        # Stream response
        full_content = ""
        async for chunk in provider.chat_completion_stream(chat_request):
            full_content += chunk.content
            
            # Format as SSE
            chunk_response = StreamChunkResponse(
                job_id=job_id,
                content=chunk.content,
                finish_reason=chunk.finish_reason,
            )
            yield f"data: {chunk_response.model_dump_json()}\n\n"
        
        # Count tokens for usage tracking
        prompt_text = " ".join([msg.content for msg in request.messages])
        prompt_tokens = provider.count_tokens(prompt_text, request.model)
        completion_tokens = provider.count_tokens(full_content, request.model)
        
        # Update job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.tokens_used = prompt_tokens + completion_tokens
            await db.commit()
        
        # Record usage
        await record_usage(
            user_id=user.id,
            job_id=job_id,
            provider=request.provider,
            model=request.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            db=db,
        )
        
        # Send final message
        yield "data: [DONE]\n\n"
    
    except Exception as e:
        # Update job status
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            await db.commit()
        
        # Send error
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"


@router.post("/stream")
async def chat_stream(
    request: ChatCompletionRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream chat completion.
    
    Args:
        request: Chat completion request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Streaming response
    """
    # Check quota
    await check_quota(current_user, db)
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=JobType.CHAT,
        prompt=request.messages[-1].content if request.messages else "",
        parameters=request.model_dump(exclude={"messages"}),
        model_name=request.model,
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    
    return StreamingResponse(
        generate_stream(request, current_user, job.id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )

