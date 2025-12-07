from fastapi import APIRouter, Depends, status
from supabase import Client

from vembedding.dependencies import get_supabase_client_no_auth, get_job_service
from .service import JobService
from .model import JobResponse, JobCreate

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    supabase: Client = Depends(get_supabase_client_no_auth),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    """Create a new job"""
    return await service.create_job(payload, supabase)
