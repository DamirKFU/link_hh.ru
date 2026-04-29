from typing import TypeVar

from jwt.exceptions import DecodeError, ExpiredSignatureError
from pydantic import BaseModel

from backend.common.auth.schemas import (
    EmailVerificationPayload,
    PasswordResetPayload,
    TokenPayload,
)
from backend.common.exceptions.errors import JWTExpiredError, JWTInvalidError
from backend.common.resources import strings
from backend.common.security.jwt_utils import get_shema_from_token

BM = TypeVar("BM", bound=BaseModel)


def _decode_jwt_token(token: str, schema: type[BM]) -> BM:
    try:
        return get_shema_from_token(token, schema)
    except ExpiredSignatureError as e:
        raise JWTExpiredError(strings.JWT_EXPIRED_ERROR) from e
    except DecodeError as e:
        raise JWTInvalidError(strings.JWT_INVALID_ERROR) from e


def decode_auth_token(token: str) -> TokenPayload:
    return _decode_jwt_token(token, TokenPayload)


def decode_password_reset_token(token: str) -> PasswordResetPayload:
    return _decode_jwt_token(token, PasswordResetPayload)


def decode_email_verification_token(token: str) -> EmailVerificationPayload:
    return _decode_jwt_token(token, EmailVerificationPayload)
