from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
