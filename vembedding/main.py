from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from vembedding.ai.embedding import (
    MAX_TOKEN_LENGTH,
    MIN_TOKEN_LENGTH,
    validate_text_length,
)

# initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# initialize app
app = FastAPI()
app.state.limiter = limiter


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
async def root():
    return {"message": "Hello World"}


@app.get("/check-token-size", tags=["Debug Endpoints"])
@limiter.limit("10/minute")
def check_token_size(request: Request, text: str):
    """Debug endpoint to check the number of tokens in a text"""
    token_count = validate_text_length(text)
    return {
        "text_length": len(text),
        "token_count": token_count,
        "is_valid": token_count >= MIN_TOKEN_LENGTH and token_count <= MAX_TOKEN_LENGTH,
    }
