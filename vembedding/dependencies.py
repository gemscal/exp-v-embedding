from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client, create_client

from vembedding.applicants.service import ApplicantService, applicant
from vembedding.jobs.service import JobService, job
from vembedding.config import settings

security = HTTPBearer()


# ========================#
# Supabase Dependencies   #
# ========================#
def get_supabase_client_no_auth() -> Client:
    """Create a supabase client without authentication"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Client:
    """Create a supabase client with auth context"""
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    token = credentials.credentials
    client.postgrest.auth(token)

    return client


def get_user_id(
    supabase: Client = Depends(get_supabase_client),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get the user ID from the credentials"""
    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Coult not verify credentials: {e}",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user.user.id


# ========================#
# Service Dependencies    #
# ========================#
def get_job_service() -> JobService:
    """Create job service instance"""
    return job


def get_applicant_service() -> ApplicantService:
    """Create applicant service instance"""
    return applicant
