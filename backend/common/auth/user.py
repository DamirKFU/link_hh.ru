from typing import Annotated

from fastapi import Depends

from backend.apps.users.cruds import users_crud
from backend.apps.users.models.users import User
from backend.apps.users.schemas.users import UserSelect
from backend.common.auth.cookies import AccessToken
from backend.common.auth.decoders import decode_auth_token
from backend.common.auth.messages import AuthMessages
from backend.common.auth.service import validate_session
from backend.common.exceptions.errors import (
    ApiHTTPException,
    JWTExpiredError,
    JWTInvalidError,
)
from backend.common.resources import constants
from backend.core.config import settings
from backend.database.db import CurrentSession
from backend.database.redis import AuthRedis


async def _get_user_from_token(
    session: CurrentSession,
    redis: AuthRedis,
    access_token: AccessToken,
) -> UserSelect:

    try:
        schema = decode_auth_token(access_token)
        await validate_session(redis, schema)
    except JWTExpiredError as e:
        raise ApiHTTPException(
            AuthMessages.JWT_EXPIRED,
            loc=(constants.COOKIE, settings.auth.refresh_cookie_name),
        ) from e
    except JWTInvalidError as e:
        raise ApiHTTPException(
            AuthMessages.JWT_INVALID,
            loc=(constants.COOKIE, settings.auth.refresh_cookie_name),
        ) from e

    user = await users_crud.get(
        session,
        schema_to_select=UserSelect,
        return_as_model=True,
        id=schema.sub,
        one_or_none=True,
    )
    if user is None:
        raise ApiHTTPException(
            AuthMessages.USER_NOT_FOUND,
            loc=(constants.COOKIE, settings.auth.refresh_cookie_name),
        )

    return user


async def get_current_active_user(
    user: Annotated[User, Depends(_get_user_from_token)],
) -> User:
    if not user.is_active:
        raise ApiHTTPException(AuthMessages.USER_INACTIVE)
    return user


async def get_current_verified_user(
    user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if not user.is_verified:
        raise ApiHTTPException(AuthMessages.USER_NOT_VERIFIED)
    return user


async def get_current_superuser(
    user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if not user.is_superuser:
        raise ApiHTTPException(AuthMessages.USER_NOT_SUPERUSER)
    return user


CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]
