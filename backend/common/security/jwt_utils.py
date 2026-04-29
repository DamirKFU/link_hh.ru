from datetime import datetime, timedelta, timezone
from typing import Any, TypeVar

import jwt
from jwt.exceptions import InvalidSignatureError
from pydantic import BaseModel, ValidationError

from backend.common.resources import strings
from backend.core.config import settings

BM = TypeVar("BM", bound=BaseModel)


def create_token(
    schema: BaseModel,
    expire_seconds: int,
) -> str:
    to_encode = schema.model_dump(mode="json")
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    return jwt.encode(
        to_encode,
        settings.core.secret_key.get_secret_value(),
        algorithm=settings.auth.token_algorithm,
    )


def _decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.core.secret_key.get_secret_value(),
        algorithms=[settings.auth.token_algorithm],
    )


def get_shema_from_token(token: str, schema: type[BM]) -> BM:
    payload = _decode_token(token)
    payload.pop("exp", None)
    try:
        return schema.model_validate(payload)
    except ValidationError as e:
        raise InvalidSignatureError(strings.JWT_INVALID_ERROR) from e
