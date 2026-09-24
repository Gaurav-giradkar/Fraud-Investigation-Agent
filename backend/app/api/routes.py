from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.cases import router as cases_router

api_router = APIRouter(prefix="/api")
api_router.include_router(cases_router)

router = APIRouter()
router.include_router(health_router)
router.include_router(api_router)
