from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class JobBase(BaseModel):
    title: str
    description: str
    requirements: str
    author: str


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    author: Optional[str] = None


class JobResponse(JobBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
