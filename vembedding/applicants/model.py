from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ApplicantBase(BaseModel):
    name: str
    email: EmailStr
    resume_text: str
    skills: str
    experience: str


class ApplicantCreate(ApplicantBase):
    pass


class ApplicantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    resume_text: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None


class ApplicantResponse(ApplicantBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    # embedding: Optional[List[float]] = None

    class Config:
        from_attributes = True
