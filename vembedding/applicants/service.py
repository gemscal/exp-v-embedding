import logging
from fastapi import HTTPException, status
from postgrest import APIError
from supabase import Client

from vembedding.constant import TableNamesConst
from vembedding.ai.embedding import openai_generate_embedding, validate_text_length
from vembedding.applicants.model import ApplicantCreate, ApplicantResponse


class ApplicantService:
    TABLE_NAME = TableNamesConst.APPLICANTS

    async def create_applicant(
        self,
        payload: ApplicantCreate,
        supabase: Client,
    ) -> ApplicantResponse:
        """Create a new applicant record"""

        # safeety checks
        combine_text = f"{payload.name} {payload.email} {payload.resume_text} {payload.skills} {payload.experience}"
        token_count = validate_text_length(combine_text)

        logging.info(f"Token count: {token_count}")

        # generate embedding for the applicant
        try:
            embedding = await openai_generate_embedding(combine_text)
            if not embedding:
                raise ValueError("Embedding generation returned empty result")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embedding: {e}",
            )

        # store the applicant in the database
        try:
            applicant_data = payload.model_dump(mode="json")
            applicant_data["embedding"] = embedding
            response = supabase.table(self.TABLE_NAME).insert(applicant_data).execute()

            if not response.data:
                raise ValueError("Datatbase insertion returned empty result")

        except (APIError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing applicant: {e}",
            )

        return response.data[0]


applicant = ApplicantService()
