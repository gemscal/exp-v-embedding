from fastapi import APIRouter, Depends, Request, status
from supabase import Client

from vembedding.rate_limiter import limiter
from vembedding.dependencies import get_applicant_service, get_supabase_client_no_auth
from .service import ApplicantService
from .model import ApplicantResponse, ApplicantCreate

router = APIRouter(
    prefix="/api/applicants",
    tags=["applicants"],
)


@limiter.limit("1/minute")
@router.post("/", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
async def create_applicant(
    request: Request,
    payload: ApplicantCreate,
    supabase: Client = Depends(get_supabase_client_no_auth),
    service: ApplicantService = Depends(get_applicant_service),
) -> ApplicantResponse:
    """Create a new applicant"""
    return await service.create_applicant(payload, supabase)
