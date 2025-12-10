from fastapi import APIRouter, Depends, Request, status
from supabase import Client

from vembedding.rate_limiter import limiter
from vembedding.dependencies import get_supabase_client_no_auth, get_job_service
from .service import JobService
from .model import JobResponse, JobCreate, SearchApplicants

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs Endpoints"],
)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def create_job(
    request: Request,
    payload: JobCreate,
    supabase: Client = Depends(get_supabase_client_no_auth),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    """Create a new job"""
    return await service.create_job(payload, supabase)


@router.post("/{job_id}/search-applicants", status_code=status.HTTP_200_OK)
@limiter.limit("1/minute")
async def search_applicants(
    request: Request,
    job_id: str,
    payload: SearchApplicants,
    supabase: Client = Depends(get_supabase_client_no_auth),
    service: JobService = Depends(get_job_service),
):
    """Search for applicants for a job"""
    return await service.search_applicants(job_id, payload, supabase)
