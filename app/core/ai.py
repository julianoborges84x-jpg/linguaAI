from fastapi import HTTPException, status
from app.core.config import settings


def require_openai_api_key() -> str:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )
    return settings.openai_api_key
