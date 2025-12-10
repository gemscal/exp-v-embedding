from fastapi import HTTPException, status
from postgrest import APIError
from supabase import Client

from vembedding.constant import TableNamesConst
from vembedding.application.model import ApplicationCreate, ApplicationResponse


class ApplicationService:
    TABLE_NAME = TableNamesConst.APPLICATIONS

    async def create_application(
        self,
        payload: ApplicationCreate,
        supabase: Client,
    ) -> ApplicationResponse:
        """Create a new application"""

        try:
            job = (
                supabase.table(TableNamesConst.JOBS)
                .select("id")
                .eq("id", payload.job_id)
                .execute()
            )
            if not job.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found",
                )

            applicant = (
                supabase.table(TableNamesConst.APPLICANTS)
                .select("id")
                .eq("id", payload.applicant_id)
                .execute()
            )
            if not applicant.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Applicant not found",
                )

            existing_application = (
                supabase.table(self.TABLE_NAME)
                .select("id")
                .eq("job_id", payload.job_id)
                .eq("applicant_id", payload.applicant_id)
                .execute()
            )
            if existing_application.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Application already exists",
                )

        except HTTPException:
            raise
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {e}",
            )

        try:
            application_data = payload.model_dump(mode="json")
            application_data["status"] = "applied"
            response = (
                supabase.table(self.TABLE_NAME).insert(application_data).execute()
            )
            if not response.data:
                raise ValueError("Database insertion returned empty result")

        except (APIError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing application: {e}",
            )

        return response.data[0]


application = ApplicationService()
