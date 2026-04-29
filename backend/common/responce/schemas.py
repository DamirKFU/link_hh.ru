from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    message: str
    message_key: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    message: str
    message_key: str
    loc: Optional[tuple[int | str, ...]] = None
    detail: Optional[str]
