from typing import Optional

from fastapi import BackgroundTasks, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.auth.email import send_reset_password_email, send_verification_email
from backend.apps.auth.messages import AuthMessages
from backend.apps.auth.schemas import (
    ForgotPassword,
    ResetPassword,
    TokenSchema,
    UserLogin,
    UserPublic,
    UserRegister,
    VerifyEmail,
)
from backend.apps.users.cruds.users import users_crud
from backend.apps.users.schemas import UserCreate, UserSelect
from backend.common.auth.dataclasses import TokenPair
from backend.common.auth.service import (
    email_verification,
    forgot_password,
    login,
    logout,
    logout_all,
    password_reset,
    refresh,
    verify_email,
)
from backend.common.email import EmailBackend
from backend.common.exceptions.errors import (
    ApiHTTPException,
    JWTExpiredError,
    JWTInvalidError,
)
from backend.common.resources import constants
from backend.common.security.hash_utils import verify_password
from backend.core.config import settings


class AuthService:
    async def register(
        self,
        session: AsyncSession,
        schema: UserRegister,
    ) -> UserPublic:
        existing = await users_crud.exists(session, email=schema.email)
        if existing:
            raise ApiHTTPException(
                AuthMessages.EMAIL_ALREADY_EXISTS,
                loc=(constants.BODY, schema.fields.email),
            )

        user = await users_crud.create_user(
            session,
            UserCreate(email=schema.email, password=schema.password),
            commit=False,
        )
        await session.commit()
        return UserPublic.model_validate(user)

    async def login(
        self,
        session: AsyncSession,
        redis: Redis,
        response: Response,
        schema: UserLogin,
    ) -> None:
        user = await users_crud.get(
            session,
            email=schema.email,
            schema_to_select=UserSelect,
            return_as_model=True,
        )
        if not user:
            raise ApiHTTPException(
                AuthMessages.INVALID_CREDENTIALS,
                loc=(constants.BODY,),
            )

        if not verify_password(schema.password, user.hashed_password):
            raise ApiHTTPException(
                AuthMessages.INVALID_CREDENTIALS,
                loc=(constants.BODY,),
            )

        tokens = await login(
            redis,
            user_id=user.id,
        )
        self._set_tokens_cookie(response, tokens)

    async def refresh(
        self,
        redis: Redis,
        response: Response,
        refresh_token: str,
    ) -> None:
        try:
            tokens = await refresh(redis, refresh_token=refresh_token)
        except (JWTExpiredError, JWTInvalidError) as e:
            raise ApiHTTPException(
                AuthMessages.JWT_INVALID,
                loc=(constants.COOKIE, settings.auth.refresh_cookie_name),
            ) from e

        self._set_tokens_cookie(response, tokens)

    async def logout(
        self,
        redis: Redis,
        response: Response,
        refresh_token: Optional[str],
    ) -> None:
        if refresh_token is not None:
            await logout(redis, refresh_token=refresh_token)

        response.delete_cookie(settings.auth.access_cookie_name)
        response.delete_cookie(settings.auth.refresh_cookie_name)

    async def forgot_password(
        self,
        session: AsyncSession,
        redis: Redis,
        mailer: EmailBackend,
        background_tasks: BackgroundTasks,
        schema: ForgotPassword,
    ) -> None:
        user = await users_crud.get(
            session,
            email=schema.email,
            schema_to_select=UserSelect,
            return_as_model=True,
        )

        if user is None:
            return

        token = await forgot_password(redis, user_id=user.id)

        send_reset_password_email(
            background_tasks=background_tasks,
            mailer=mailer,
            email=schema.email,
            token=token,
        )

    async def reset_password(
        self,
        session: AsyncSession,
        redis: Redis,
        schema: ResetPassword,
    ) -> None:
        try:
            user_id = await password_reset(redis, schema.token)
        except (JWTExpiredError, JWTInvalidError) as e:
            raise ApiHTTPException(
                AuthMessages.JWT_INVALID,
                loc=(constants.BODY, schema.fields.token),
            ) from e

        user = await users_crud.get(
            session, id=user_id, schema_to_select=UserSelect, return_as_model=True
        )
        if not user:
            raise ApiHTTPException(
                AuthMessages.USER_NOT_FOUND,
                loc=(constants.BODY, schema.fields.token),
            )

        await logout_all(redis, user_id=user.id)

        await users_crud.change_password(
            session,
            user_id=user.id,
            password=schema.password,
        )

    async def send_verification(
        self,
        mailer: EmailBackend,
        background_tasks: BackgroundTasks,
        schema: VerifyEmail,
    ) -> None:
        token = await email_verification(schema.email)
        send_verification_email(
            background_tasks=background_tasks,
            mailer=mailer,
            email=schema.email,
            token=token,
        )

    async def confirm_email(
        self,
        session: AsyncSession,
        schema: TokenSchema,
    ) -> None:
        try:
            email = await verify_email(schema.token)
        except (JWTExpiredError, JWTInvalidError) as e:
            raise ApiHTTPException(
                AuthMessages.JWT_INVALID,
                loc=(constants.BODY, schema.fields.token),
            ) from e

        user = await users_crud.get(
            session,
            email=email,
            schema_to_select=UserSelect,
            return_as_model=True,
        )
        if not user:
            raise ApiHTTPException(
                AuthMessages.USER_NOT_FOUND,
                loc=(constants.BODY, schema.fields.token),
            )

        if user.is_verified:
            return

        await users_crud.set_verify(session, user_id=user.id)

    @staticmethod
    def _set_tokens_cookie(response: Response, tokens: TokenPair) -> None:
        response.set_cookie(
            key=settings.auth.access_cookie_name,
            value=tokens.access_token,
            httponly=settings.auth.cookie_httponly,
            secure=settings.auth.cookie_secure,
            samesite=settings.auth.cookie_samesite,
            max_age=settings.auth.access_token_expire_seconds,
        )
        response.set_cookie(
            key=settings.auth.refresh_cookie_name,
            value=tokens.refresh_token,
            httponly=settings.auth.cookie_httponly,
            secure=settings.auth.cookie_secure,
            samesite=settings.auth.cookie_samesite,
            max_age=settings.auth.refresh_token_expire_seconds,
        )


auth_service = AuthService()
