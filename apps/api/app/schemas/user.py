"""User schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    google_id: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = None
    picture: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

