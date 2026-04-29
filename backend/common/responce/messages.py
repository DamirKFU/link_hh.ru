from dataclasses import dataclass
from typing import NamedTuple

from fastapi_babel import lazy_gettext as _l
from starlette import status


class Msg(NamedTuple):
    key: _l
    code: int = status.HTTP_200_OK


@dataclass
class MessagesBase:
    # 2xx
    SUCCESS = Msg(_l("SUCCESS"), status.HTTP_200_OK)
    NOCONTENT = Msg(_l("SUCCESS"), status.HTTP_204_NO_CONTENT)
    CREATED = Msg(_l("CREATED"), status.HTTP_201_CREATED)

    # 4xx
    ERROR = Msg(_l("ERROR"), status.HTTP_400_BAD_REQUEST)
    UNAUTHORIZED = Msg(_l("UNAUTHORIZED"), status.HTTP_401_UNAUTHORIZED)
    FORBIDDEN = Msg(_l("FORBIDDEN"), status.HTTP_403_FORBIDDEN)
    CSRF_FORBIDDEN = Msg(_l("CSRF_FORBIDDEN"), status.HTTP_403_FORBIDDEN)
    NOT_FOUND = Msg(_l("NOT_FOUND"), status.HTTP_404_NOT_FOUND)
    CONFLICT = Msg(_l("CONFLICT"), status.HTTP_409_CONFLICT)
    VALIDATION_ERROR = Msg(
        _l("VALIDATION_ERROR"), status.HTTP_422_UNPROCESSABLE_CONTENT
    )

    # 5xx
    INTERNAL_ERROR = Msg(_l("INTERNAL_ERROR"), status.HTTP_500_INTERNAL_SERVER_ERROR)
