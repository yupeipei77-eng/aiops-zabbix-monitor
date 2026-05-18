from fastapi import Header, HTTPException
from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key != settings.WEBHOOK_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
