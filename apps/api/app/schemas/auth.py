"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel

from .user import UserResponse


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OAuthCallbackRequest(BaseModel):
    """Schema for OAuth callback request."""

    code: str
    state: Optional[str] = None


class OAuthURLResponse(BaseModel):
    """Schema for OAuth URL response."""

    url: str

