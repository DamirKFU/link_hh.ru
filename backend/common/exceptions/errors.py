from typing import Mapping

from fastapi import HTTPException

from backend.common.responce.messages import Msg


class SendEmailError(Exception):
    """Ошибка отправки сообщения."""


class JWTInvalidError(Exception):
    """Неверный токен."""


class JWTExpiredError(Exception):
    """Токен истек."""


class SessionExpiredError(Exception):
    """Сессия не найдена или истекла."""


class ApiHTTPException(HTTPException):
    def __init__(
        self,
        msg: Msg,
        loc: tuple[int | str, ...] | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        self.msg = msg
        self.loc = loc

        super().__init__(
            status_code=msg.code,
            detail=msg.key.message,
            headers=headers,
        )
