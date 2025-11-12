"""Health check routes."""

import os
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "pulse-api",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint - checks if service is ready to accept traffic.
    
    Args:
        db: Database session
        
    Returns:
        Readiness status with component checks
    """
    components = {}
    is_ready = True
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = {"status": "up", "message": "Connected"}
    except Exception as e:
        components["database"] = {"status": "down", "message": str(e)}
        is_ready = False
    
    # Check S3 (optional - just check if configured)
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    if s3_bucket:
        components["s3"] = {"status": "configured", "bucket": s3_bucket}
    else:
        components["s3"] = {"status": "not_configured"}
    
    # Check SQS (optional - just check if configured)
    sqs_queue = os.getenv("SQS_QUEUE_URL")
    if sqs_queue:
        components["sqs"] = {"status": "configured", "queue": sqs_queue}
    else:
        components["sqs"] = {"status": "not_configured"}
    
    # Check Stripe (optional)
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if stripe_key:
        components["stripe"] = {"status": "configured"}
    else:
        components["stripe"] = {"status": "not_configured"}
    
    status_code = 200 if is_ready else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
        }
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint - checks if service is alive.
    
    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check endpoint (legacy).
    
    Args:
        db: Database session
        
    Returns:
        Database health status
    """
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }

