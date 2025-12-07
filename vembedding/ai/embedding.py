from typing import List
from fastapi import HTTPException, status
from openai import AsyncOpenAI
from tiktoken import get_encoding

from vembedding.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
ENCODING = get_encoding("cl100k_base")
MAX_TOKEN_LENGTH = 8000
MIN_TOKEN_LENGTH = 10


async def openai_generate_embedding(text: str) -> List[float]:
    """openAI generate embedding"""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    print(response)
    return response.data[0].embedding


def count_tokens(text: str) -> int:
    """count the number of tokens"""
    return len(ENCODING.encode(text))


def validate_text_length(text: str) -> int:
    """validate the length of the text"""
    token_count = count_tokens(text)
    if token_count < MIN_TOKEN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text is too short. Minimum {MIN_TOKEN_LENGTH} tokens required.",
        )
    if token_count > MAX_TOKEN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text is too long. Maximum {MAX_TOKEN_LENGTH} tokens allowed.",
        )

    return token_count
