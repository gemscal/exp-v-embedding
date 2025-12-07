from .model import JobCreate, JobResponse
from supabase import Client


class JobService:
    TABLE_NAME = "jobs"

    def create_job(self, payload: JobCreate, supabase: Client) -> JobResponse:
        """Create a new job"""
        return supabase.table(self.TABLE_NAME).insert(payload.model_dump()).execute()


job = JobService()
