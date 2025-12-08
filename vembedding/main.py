import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from vembedding.ai.embedding import (
    MAX_TOKEN_LENGTH,
    MIN_TOKEN_LENGTH,
    validate_text_length,
)
from vembedding.jobs.routes import router as jobs_router
from .rate_limiter import limiter


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - %(message)s - %(asctime)s - %(name)s"
)

# initialize app
app = FastAPI()
app.state.limiter = limiter


# handle rate limit exceeded exceptions
@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    """Rate limit exceeded exception handler"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
            "endpoint": str(request.url.path),
        },
        headers=exc.headers,
    )


@app.get("/")
def root():
    return {"message": "Hello World"}


@limiter.limit("10/minute")
@app.get("/check-token-size", tags=["Debug Endpoints"])
def check_token_size(request: Request, text: str):
    """Debug endpoint to check the number of tokens in a text"""
    token_count = validate_text_length(text)
    return {
        "text_length": len(text),
        "token_count": token_count,
        "is_valid": token_count >= MIN_TOKEN_LENGTH and token_count <= MAX_TOKEN_LENGTH,
    }


# include routers
app.include_router(jobs_router)
