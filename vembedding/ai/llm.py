import json
from typing import Dict, List
from fastapi import HTTPException, status
from openai import AsyncOpenAI, OpenAIError

from vembedding.config import settings
from vembedding.constant import LLMModelsConst

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
LLM_MODEL = LLMModelsConst.OPENAI_LLM_MODEL


async def generate_search_explanation(
    job_info: Dict,
    candidates: List[Dict],
    query: str,
) -> Dict:
    """
    Generate an AI-powered analysis report for candidate applicants.
    """

    system_prompt = """
        You are an expert technical recruiter and talent analyst with 15+ years of experience.

        Your role is to:
        1. Analyze candidate profiles against job requirements
        2. Provide objective, evidence-based assessments
        3. Identify both strengths and potential concerns
        4. Give actionable hiring recommendations

        Key principles:
        - Be specific and cite evidence from the candidate's profile
        - Consider both technical skills and soft skills
        - Highlight relevant experience, not just keywords
        - Be honest about gaps or concerns
        - Use professional, neutral language
        - Focus on job-relevance
    """

    user_prompt = f"""
        # Job Context:
        - **Job Title:** {job_info['title']}
        - **Job Description:** {job_info['description']}
        - **Requirements:** {job_info['requirements']}

        ---
        # Recruiter's Search Query
        "{query}"
        ---

        Task
        Analyze the following candidates and explain why they match (or don't match) the search criteria and job requirements.

        Candidates to Analyze
    """
    for idx, candidate in enumerate(candidates, 1):
        # Truncate resume at word boundary to avoid cutting mid-word
        resume_preview = candidate["resume_text"][:800]
        if len(candidate["resume_text"]) > 800:
            resume_preview = resume_preview.rsplit(" ", 1)[0] + "..."

        user_prompt += f"""
        ## Candidate {idx}: {candidate['name']} (ID: {candidate['id']})
        - **Email:** {candidate['email']}
        - **Similarity Score:** {candidate['similarity_score']:.3f}
        - **Skills:** {candidate['skills']}
        - **Experience:** {candidate['experience']}
        - **Resume Summary:** {resume_preview}
        """

    # Specify exact output format
    user_prompt += """
        ---

        # Output Format
        Return a JSON object with this exact structure:

        {
        "overall_summary": "2-3 sentence summary of the candidate pool quality",
        "candidates": [
            {
            "candidate_id": "Use the exact ID from the candidate input",
            "candidate_name": "Use the exact name from the candidate input",
            "similarity_score": 0.XX,
            "match_quality": "Excellent Match" | "Strong Match" | "Good Match" | "Moderate Match" | "Weak Match",
            "match_explanation": "2-3 sentences explaining why this candidate matches. Be specific and cite evidence.",
            "key_strengths": [
                "Specific strength 1 with evidence",
                "Specific strength 2 with evidence",
                "Specific strength 3 with evidence"
            ],
            "potential_concerns": [
                "Specific concern 1 (or empty array if none)",
                "Specific concern 2 (or empty array if none)"
            ],
            "relevant_experience_highlights": [
                "Relevant experience point 1",
                "Relevant experience point 2"
            ],
            "hiring_recommendation": "Strong recommendation with specific next steps"
            }
        ]
        }

        # Guidelines
        1. Use the EXACT candidate_id and candidate_name from the input data provided above
        2. Base analysis ONLY on provided information
        3. Be specific - cite actual skills and achievements
        4. Consider similarity score but don't rely on it alone
        5. Match quality should reflect alignment with BOTH query and job requirements
        6. Provide actionable recommendations
    """

    try:
        # Calculate dynamic max_tokens based on number of candidates
        # ~400 tokens per candidate analysis + 1000 for summary and overhead
        dynamic_max_tokens = min(8192, 400 * len(candidates) + 1000)

        # Generate the analysis report
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=dynamic_max_tokens,
            response_format={
                "type": "json_object",
            },
        )

        # Parse the JSON string response into a Python dict
        response_content = response.choices[0].message.content
        try:
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse AI response as JSON: {str(e)}",
            )

    except OpenAIError as e:
        # Handle OpenAI-specific errors (rate limits, API errors, etc.)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI API error: {str(e)}",
        )
    except json.JSONDecodeError:
        # Re-raise JSON decode errors (already handled above)
        raise
    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error generating search explanation: {str(e)}",
        )
