"""Shared constants for the application"""


class TableNamesConst:
    """Database table names"""

    JOBS = "jobs"
    APPLICANTS = "applicants"
    APPLICATIONS = "applications"


class RateLimitsConst:
    """Rate limits for the application"""

    DEFAULT = "10/minute"
    EMBEDDING = "5/minute"


class EmbeddingModelsConst:
    """Embedding models for the application"""

    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"


class LLMModelsConst:
    """LLM models for the application"""

    OPENAI_LLM_MODEL = "gpt-4o-mini"
