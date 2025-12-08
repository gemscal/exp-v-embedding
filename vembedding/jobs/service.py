import logging
from fastapi import HTTPException, status
from postgrest import APIError
from pydantic import ValidationError
from supabase import Client

from vembedding.ai.embedding import openai_generate_embedding, validate_text_length
from .model import JobCreate, JobResponse


class JobService:
    TABLE_NAME = "jobs"

    async def create_job(self, payload: JobCreate, supabase: Client) -> JobResponse:
        """Create a new job"""

        # safety checks
        combine_text = f"{payload.title} {payload.description} {payload.requirements}"
        token_count = validate_text_length(combine_text)

        logging.info(f"Token count: {token_count}")

        # generate embedding for the job post
        try:
            embedding = await openai_generate_embedding(combine_text)
            if not embedding:
                raise ValueError("Embedding generation returned empty result")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embedding: {e}",
            )

        # store the job post in the database
        try:
            job_data = payload.model_dump(mode="json")
            job_data["embedding"] = embedding
            response = supabase.table(self.TABLE_NAME).insert(job_data).execute()

            if not response.data:
                raise ValueError("Database insertion returned empty result")

        except (APIError, ValueError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing job post: {e}",
            )

        return JobResponse(**response.data[0])


job = JobService()
