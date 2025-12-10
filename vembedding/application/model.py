from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ApplicationBase(BaseModel):
    job_id: UUID
    applicant_id: UUID
    status: str


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    job_id: Optional[UUID] = None
    applicant_id: Optional[UUID] = None
    status: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: UUID
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
