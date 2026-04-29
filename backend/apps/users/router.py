from fastapi import APIRouter

from backend.apps.users.api import v1_router

router = APIRouter(prefix="/users")


router.include_router(v1_router)
