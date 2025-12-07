from typing import List
from openai import AsyncOpenAI

from vembedding.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def openai_generate_embedding(text: str) -> List[float]:
    """openAI generate embedding"""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    print(response)
    return response.data[0].embedding
