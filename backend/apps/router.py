from fastapi import APIRouter

from backend.apps.auth.router import router as auth_router
from backend.apps.users.router import router as users_router

router = APIRouter(prefix="/api")

router.include_router(
    auth_router,
    tags=["auth"],
)
router.include_router(
    users_router,
    tags=["users"],
)
