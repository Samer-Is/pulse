"""Authentication routes."""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..models.subscription import Subscription, PlanType, SubscriptionStatus
from ..schemas.auth import TokenResponse, OAuthCallbackRequest, OAuthURLResponse
from ..auth.oauth import get_google_oauth_url, verify_google_token
from ..auth.jwt import create_access_token

router = APIRouter()


@router.get("/google", response_model=OAuthURLResponse)
async def get_google_auth_url() -> OAuthURLResponse:
    """
    Get Google OAuth authorization URL.
    
    Returns:
        URL to redirect user for Google OAuth
    """
    url = get_google_oauth_url(state=str(uuid.uuid4()))
    return OAuthURLResponse(url=url)


@router.post("/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    request: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Handle Google OAuth callback.
    
    Args:
        request: OAuth callback request with authorization code
        db: Database session
        
    Returns:
        Access token and user information
    """
    # Verify Google token and get user info
    google_user = await verify_google_token(request.code)
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.google_id == google_user["id"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == google_user["email"])
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Link Google account to existing user
            existing_user.google_id = google_user["id"]
            existing_user.name = google_user.get("name") or existing_user.name
            existing_user.picture = google_user.get("picture") or existing_user.picture
            existing_user.is_verified = google_user.get("verified_email", False)
            existing_user.last_login = datetime.utcnow()
            user = existing_user
        else:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=google_user["email"],
                name=google_user.get("name"),
                picture=google_user.get("picture"),
                google_id=google_user["id"],
                is_verified=google_user.get("verified_email", False),
                last_login=datetime.utcnow(),
            )
            db.add(user)
            
            # Create starter subscription
            now = datetime.utcnow()
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user.id,
                plan=PlanType.STARTER,
                status=SubscriptionStatus.ACTIVE,
                period_start=now,
                period_end=now + timedelta(days=30),
            )
            db.add(subscription)
    else:
        # Update existing user
        user.last_login = datetime.utcnow()
        user.name = google_user.get("name") or user.name
        user.picture = google_user.get("picture") or user.picture
    
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Import here to avoid circular import
    from ..schemas.user import UserResponse
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Note: With JWT, actual logout is handled client-side by removing the token.
    This endpoint exists for API completeness and potential future server-side logic.
    """
    return {"message": "Successfully logged out"}

