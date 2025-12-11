import logging
import time
from fastapi import HTTPException, status
from postgrest import APIError
from supabase import Client

from vembedding.constant import TableNamesConst
from vembedding.ai.llm import generate_search_explanation
from vembedding.ai.embedding import openai_generate_embedding, validate_text_length
from .model import JobCreate, JobResponse, SearchApplicants


class JobService:
    TABLE_NAME = TableNamesConst.JOBS

    async def create_job(
        self,
        payload: JobCreate,
        supabase: Client,
    ) -> JobResponse:
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

        except (APIError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing job post: {e}",
            )

        return response.data[0]

    async def search_applicants(
        self,
        job_id: str,
        payload: SearchApplicants,
        supabase: Client,
    ):
        """Search applicants inside a job post"""

        try:
            job = supabase.table(self.TABLE_NAME).select("*").eq("id", job_id).execute()
            if not job.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with id {job_id} not found",
                )

            # start_total = time.time()
            # start_embedding = time.time()
            query_embedding = await openai_generate_embedding(payload.query)
            # embedding_time = (time.time() - start_embedding) * 1000
            # print(f"⏱️ Embedding generation: {embedding_time:.0f}ms")
            if not query_embedding:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error generating query embedding",
                )

            # start_db = time.time()
            response = supabase.rpc(
                "search_applicants_for_job",
                {
                    "job_id_param": job_id,
                    "query_embedding": query_embedding,
                },
            ).execute()
            # db_time = (time.time() - start_db) * 1000
            # print(f"⏱️ Database query: {db_time:.0f}ms")
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error searching applicants inside job",
                )

            # get explanation based on the user query
            job_info = job.data[0]
            candidates = response.data
            ai_analysis = None
            if candidates:
                ai_analysis = await generate_search_explanation(
                    job_info=job_info,
                    candidates=candidates,
                    query=payload.query,
                )

        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {e}",
            )
        except HTTPException as e:
            raise

        # total_time = (time.time() - start_total) * 1000
        # print(f"⏱️ Total time: {total_time:.0f}ms")
        return {
            "job_id": job_id,
            "job_title": job_info["title"],
            "query": payload.query,
            "total_candidates": len(candidates),
            "results": candidates,
            "ai_analysis": ai_analysis,
        }


job = JobService()
