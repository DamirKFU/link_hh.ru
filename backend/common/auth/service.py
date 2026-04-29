from uuid import UUID, uuid4

from redis.asyncio import Redis

from backend.common.auth.dataclasses import TokenPair
from backend.common.auth.decoders import (
    decode_auth_token,
    decode_email_verification_token,
    decode_password_reset_token,
)
from backend.common.auth.schemas import (
    EmailVerificationPayload,
    PasswordResetPayload,
    TokenPayload,
)
from backend.common.auth.session import reset_sessions, sessions
from backend.common.exceptions.errors import (
    JWTExpiredError,
    JWTInvalidError,
)
from backend.common.resources import constants, strings
from backend.common.security.jwt_utils import create_token
from backend.core.config import settings


async def _issue_token_pair(redis: Redis, user_id: UUID) -> TokenPair:
    schema = TokenPayload(sub=user_id, session_uuid=uuid4())
    await sessions.set(
        redis,
        constants.REDIS_SESSION_UNUSED_VALUE,
        *schema.as_str_tuple,
    )
    return TokenPair(
        access_token=create_token(schema, settings.auth.access_token_expire_seconds),
        refresh_token=create_token(schema, settings.auth.refresh_token_expire_seconds),
    )


async def validate_session(redis: Redis, schema: TokenPayload) -> None:
    user_id, session_uuid = schema.as_str_tuple
    value = await sessions.get(redis, user_id, session_uuid)

    if value is None:
        raise JWTExpiredError(strings.JWT_SESSION_EXPIRED_ERROR)

    if value == constants.REDIS_SESSION_USED_VALUE:
        await logout_all(redis, schema.sub)
        raise JWTInvalidError(strings.JWT_SESSION_REUSED)


async def login(redis: Redis, user_id: UUID) -> TokenPair:
    return await _issue_token_pair(redis, user_id)


async def refresh(redis: Redis, refresh_token: str) -> TokenPair:
    schema = decode_auth_token(refresh_token)
    await validate_session(redis, schema)
    await sessions.set_used(redis, *schema.as_str_tuple)
    return await _issue_token_pair(redis, schema.sub)


async def logout(redis: Redis, refresh_token: str) -> None:
    try:
        schema = decode_auth_token(refresh_token)
        await sessions.delete(redis, *schema.as_str_tuple)
    except (JWTExpiredError, JWTInvalidError):
        return


async def logout_all(redis: Redis, user_id: UUID) -> None:
    await sessions.delete_all(redis, str(user_id))


async def forgot_password(redis: Redis, user_id: UUID) -> str:
    schema = PasswordResetPayload(sub=user_id)
    token = create_token(schema, settings.auth.password_reset_expire_seconds)
    await reset_sessions.set(redis, token, schema.user_id_str)
    return token


async def password_reset(redis: Redis, token: str) -> UUID:
    schema = decode_password_reset_token(token)
    stored = await reset_sessions.get(redis, schema.user_id_str)

    if not stored or stored != token:
        raise JWTInvalidError(strings.JWT_INVALID_ERROR)

    await reset_sessions.delete(redis, schema.user_id_str)
    return schema.sub


async def email_verification(email: str) -> str:
    schema = EmailVerificationPayload(sub=email)
    return create_token(schema, settings.auth.email_verification_expire_seconds)


async def verify_email(token: str) -> str:
    schema = decode_email_verification_token(token)
    return schema.sub
