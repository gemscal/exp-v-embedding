from fastapi import APIRouter, Depends, Request, status
from supabase import Client

from vembedding.rate_limiter import limiter
from vembedding.dependencies import get_supabase_client_no_auth, get_application_service
from .model import ApplicationResponse, ApplicationCreate
from .service import ApplicationService


router = APIRouter(
    prefix="/api/applications",
    tags=["applications"],
)


@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("1/minute")
def create_application(
    request: Request,
    payload: ApplicationCreate,
    supabase: Client = Depends(get_supabase_client_no_auth),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    """Create a new application"""
    return service.create_application(payload, supabase)
