# backend/common/responce/exception_handlers.py
from fastapi import FastAPI, Request, Response

from backend.common.exceptions.errors import ApiHTTPException
from backend.common.responce.helpers import error
from backend.common.responce.messages import MessagesBase
from backend.core.config import settings


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiHTTPException)
    async def api_http_exception_handler(
        request: Request, exc: ApiHTTPException
    ) -> Response:
        return error(
            msg=exc.msg,
            loc=exc.loc,
            detail=str(exc) if settings.core.debug else None,
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception) -> Response:
        msg = MessagesBase.INTERNAL_ERROR

        return error(
            msg=msg,
            detail=str(exc) if settings.core.debug else None,
        )
