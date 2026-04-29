from typing import Optional, TypeVar

from backend.common.responce.base import MsgSpecJSONResponse
from backend.common.responce.messages import Msg
from backend.common.responce.schemas import ErrorResponse, SuccessResponse

T = TypeVar("T")


def success(msg: Msg, data: Optional[T] = None) -> MsgSpecJSONResponse:
    body = SuccessResponse(
        message=str(msg.key),
        message_key=msg.key.message,
        data=data,
    )
    return MsgSpecJSONResponse(
        status_code=msg.code,
        content=body.model_dump(),
    )


def error(
    msg: Msg,
    loc: tuple[int | str, ...] | None = None,
    detail: Optional[str] = None,
) -> MsgSpecJSONResponse:
    body = ErrorResponse(
        message=str(msg.key),
        message_key=msg.key.message,
        loc=loc,
        detail=detail,
    )
    return MsgSpecJSONResponse(
        status_code=msg.code,
        content=body.model_dump(),
    )
