"""Authentication schemas."""

from pydantic import BaseModel, EmailStr


class MagicLinkRequest(BaseModel):
    """Request schema for magic link generation."""
    email: EmailStr
    locale: str = "ar"


class MagicLinkResponse(BaseModel):
    """Response schema for magic link generation."""
    message: str
    email: str


class VerifyMagicLinkRequest(BaseModel):
    """Request schema for magic link verification."""
    token: str


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: dict

