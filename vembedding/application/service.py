from supabase import Client
from vembedding.application.model import ApplicationCreate, ApplicationResponse


class ApplicationService:
    TABLE_NAME = "applications"

    async def create_application(
        self,
        payload: ApplicationCreate,
        supabase: Client,
    ) -> ApplicationResponse:
        """Create a new application"""
        return await super().create_application(payload, supabase)


application = ApplicationService()
