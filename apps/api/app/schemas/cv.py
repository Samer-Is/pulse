"""CV/Resume schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class PersonalInfo(BaseModel):
    """Personal information section."""

    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    linkedin: Optional[str] = Field(None, max_length=200)
    github: Optional[str] = Field(None, max_length=200)


class Experience(BaseModel):
    """Work experience entry."""

    job_title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: str = Field(..., description="e.g., 'Jan 2020' or '2020'")
    end_date: Optional[str] = Field(None, description="e.g., 'Dec 2022' or 'Present'")
    description: Optional[str] = Field(None, max_length=1000)
    responsibilities: Optional[List[str]] = Field(None, description="List of bullet points")


class Education(BaseModel):
    """Education entry."""

    degree: str = Field(..., min_length=1, max_length=100)
    institution: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = Field(None)
    end_date: Optional[str] = Field(None)
    gpa: Optional[str] = Field(None, max_length=20)
    achievements: Optional[List[str]] = Field(None)


class Skill(BaseModel):
    """Skill entry."""

    category: Optional[str] = Field(None, max_length=50, description="e.g., 'Programming Languages'")
    skills: List[str] = Field(..., min_items=1, description="List of skills")


class CVRequest(BaseModel):
    """CV generation request."""

    personal_info: PersonalInfo
    summary: Optional[str] = Field(None, max_length=500, description="Professional summary")
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    format: str = Field("docx", description="Export format: docx or pdf")
    template: Optional[str] = Field("modern", description="Template style: modern, classic, minimal")


class CVResponse(BaseModel):
    """CV generation response."""

    job_id: str
    format: str
    download_url: str
    s3_key: str
    expires_at: str

