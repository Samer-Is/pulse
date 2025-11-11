"""CV generation schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class CVEducation(BaseModel):
    """Education entry."""
    degree: str
    institution: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None


class CVExperience(BaseModel):
    """Work experience entry."""
    title: str
    company: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    description: str


class CVGenerateRequest(BaseModel):
    """Request schema for CV generation."""
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    title: str
    summary: str
    skills: List[str]
    education: List[CVEducation]
    experience: List[CVExperience]
    locale: str = "ar"
    ats_friendly: bool = True
    export_format: str = "pdf"  # pdf or docx


class CVGenerateResponse(BaseModel):
    """Response schema for CV generation."""
    cv_id: str
    status: str
    download_url: str
    preview_url: Optional[str] = None
    format: str

