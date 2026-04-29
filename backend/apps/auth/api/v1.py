from fastapi import APIRouter, BackgroundTasks, Response
from starlette import status

from backend.apps.auth.schemas import (
    ForgotPassword,
    ResetPassword,
    TokenSchema,
    UserLogin,
    UserPublic,
    UserRegister,
    VerifyEmail,
)
from backend.apps.auth.services.auth import auth_service
from backend.common.auth.cookies import OptionalRefreshToken, RefreshToken
from backend.common.email import EmailBackendDep
from backend.common.responce import MessagesBase, SuccessResponse, success
from backend.database.db import CurrentSession
from backend.database.redis import AuthRedis

router = APIRouter(prefix="/v1")


@router.post("/register", response_model=SuccessResponse[UserPublic])
async def register(
    session: CurrentSession,
    schema: UserRegister,
) -> Response:
    data = await auth_service.register(session, schema)
    return success(
        msg=MessagesBase.SUCCESS,
        data=data,
    )


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    session: CurrentSession,
    redis: AuthRedis,
    response: Response,
    schema: UserLogin,
) -> None:
    await auth_service.login(
        session=session,
        redis=redis,
        response=response,
        schema=schema,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    redis: AuthRedis,
    response: Response,
    refresh_token: OptionalRefreshToken,
) -> None:
    await auth_service.logout(
        redis=redis,
        response=response,
        refresh_token=refresh_token,
    )


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(
    redis: AuthRedis,
    response: Response,
    refresh_token: RefreshToken,
) -> None:
    await auth_service.refresh(
        redis=redis,
        response=response,
        refresh_token=refresh_token,
    )


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    session: CurrentSession,
    redis: AuthRedis,
    mailer: EmailBackendDep,
    background: BackgroundTasks,
    schema: ForgotPassword,
) -> None:
    await auth_service.forgot_password(
        redis=redis,
        mailer=mailer,
        session=session,
        background_tasks=background,
        schema=schema,
    )


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    session: CurrentSession,
    redis: AuthRedis,
    schema: ResetPassword,
) -> None:
    await auth_service.reset_password(
        redis=redis,
        session=session,
        schema=schema,
    )


@router.post("/send-verification", status_code=status.HTTP_204_NO_CONTENT)
async def send_verification(
    mailer: EmailBackendDep,
    background: BackgroundTasks,
    schema: VerifyEmail,
) -> None:
    await auth_service.send_verification(
        mailer=mailer,
        background_tasks=background,
        schema=schema,
    )


@router.post("/confirm-email", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_email(
    session: CurrentSession,
    schema: TokenSchema,
) -> None:
    await auth_service.confirm_email(
        session=session,
        schema=schema,
    )
