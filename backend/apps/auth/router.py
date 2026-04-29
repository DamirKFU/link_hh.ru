from fastapi import APIRouter

from backend.apps.auth.api import v1_router

router = APIRouter(prefix="/auth")

router.include_router(
    v1_router,
)
