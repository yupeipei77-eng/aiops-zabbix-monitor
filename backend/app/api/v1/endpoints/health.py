from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
        "message": "",
    }
