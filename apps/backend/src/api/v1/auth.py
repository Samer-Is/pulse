"""
Authentication routes - Magic link authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import boto3
from datetime import datetime

from ...core import get_db, get_logger, create_magic_link_token, verify_magic_link_token, create_access_token, get_current_user
from ...core.config import get_settings
from ...models import User

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


# Schemas
class MagicLinkRequest(BaseModel):
    email: EmailStr
    locale: str = "ar"


class MagicLinkVerifyRequest(BaseModel):
    token: str


class AuthResponse(BaseModel):
    user: dict
    subscription: dict | None
    redirect_url: str


# Routes
@router.post("/magic-link")
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Request a magic link to be sent to the user's email.
    Creates user if they don't exist.
    """
    logger.info(f"Magic link requested for {request.email}")
    
    # Get or create user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        user = User(
            email=request.email,
            locale=request.locale,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {user.id}")
    
    # Generate magic link token
    token = create_magic_link_token(request.email)
    magic_link = f"{settings.FRONTEND_URL}/verify?token={token}"
    
    # Send email via SES
    try:
        ses_client = boto3.client('ses', region_name=settings.SES_REGION)
        
        subject = "تسجيل الدخول إلى Pulse AI Studio" if request.locale == "ar" else "Sign in to Pulse AI Studio"
        body = f"""
        {"مرحبًا" if request.locale == "ar" else "Hello"},
        
        {"انقر على الرابط أدناه لتسجيل الدخول" if request.locale == "ar" else "Click the link below to sign in"}:
        
        {magic_link}
        
        {"هذا الرابط صالح لمدة 10 دقائق" if request.locale == "ar" else "This link expires in 10 minutes"}.
        
        {"إذا لم تطلب هذا البريد، تجاهله" if request.locale == "ar" else "If you didn't request this, ignore this email"}.
        
        {"شكرًا" if request.locale == "ar" else "Thanks"},
        Pulse AI Studio
        """
        
        ses_client.send_email(
            Source=settings.EMAIL_FROM,
            Destination={'ToAddresses': [request.email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        
        logger.info(f"Magic link sent to {request.email}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link email"
        )
    
    return {
        "data": {
            "message": f"Magic link sent to {request.email}",
            "expires_in": 600
        }
    }


@router.post("/magic-link/verify", response_model=AuthResponse)
async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify magic link token and issue JWT session cookie.
    """
    # Verify token and extract email
    email = verify_magic_link_token(request.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link token"
        )
    
    # Get user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=settings.JWT_EXPIRE_MINUTES * 60
    )
    
    logger.info(f"User authenticated: {user.id}")
    
    # Get subscription info
    subscription_info = None
    if user.subscription:
        subscription_info = {
            "plan_name": user.subscription.plan.name,
            "status": user.subscription.status,
            "renews_at": user.subscription.renews_at.isoformat() if user.subscription.renews_at else None
        }
    
    return {
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "locale": user.locale,
                "created_at": user.created_at.isoformat()
            },
            "subscription": subscription_info,
            "redirect_url": "/app/chat"
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing session cookie."""
    response.delete_cookie("session")
    
    return {
        "data": {
            "message": "Logged out successfully"
        }
    }


@router.get("/me")
async def get_current_user_info(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    
    subscription_info = None
    if user.subscription:
        subscription_info = {
            "plan_name": user.subscription.plan.name,
            "price_jod": float(user.subscription.plan.price_jod),
            "status": user.subscription.status,
            "renews_at": user.subscription.renews_at.isoformat() if user.subscription.renews_at else None
        }
    
    return {
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "locale": user.locale,
                "created_at": user.created_at.isoformat()
            },
            "subscription": subscription_info
        }
    }
