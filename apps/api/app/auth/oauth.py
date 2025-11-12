"""Google OAuth authentication."""

import os
from typing import Optional
import httpx
from fastapi import HTTPException, status

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_oauth_url(state: Optional[str] = None) -> str:
    """
    Generate Google OAuth URL.
    
    Args:
        state: Optional state parameter for CSRF protection
        
    Returns:
        Google OAuth authorization URL
    """
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    if state:
        params["state"] = state
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{GOOGLE_AUTH_URL}?{query_string}"


async def exchange_code_for_token(code: str) -> dict:
    """
    Exchange authorization code for access token.
    
    Args:
        code: Authorization code from Google
        
    Returns:
        Token response from Google
        
    Raises:
        HTTPException: If token exchange fails
    """
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )
        
        return response.json()


async def get_user_info(access_token: str) -> dict:
    """
    Get user information from Google.
    
    Args:
        access_token: Google access token
        
    Returns:
        User information from Google
        
    Raises:
        HTTPException: If fetching user info fails
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user information",
            )
        
        return response.json()


async def verify_google_token(code: str) -> dict:
    """
    Verify Google authorization code and get user info.
    
    Args:
        code: Authorization code from Google
        
    Returns:
        User information containing:
            - id: Google user ID
            - email: User email
            - name: User name
            - picture: Profile picture URL
            - verified_email: Email verification status
    """
    # Exchange code for token
    token_response = await exchange_code_for_token(code)
    access_token = token_response.get("access_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token in response",
        )
    
    # Get user information
    user_info = await get_user_info(access_token)
    
    return {
        "id": user_info.get("id"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "verified_email": user_info.get("verified_email", False),
    }

