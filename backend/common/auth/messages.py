from dataclasses import dataclass

from fastapi_babel import lazy_gettext as _l
from starlette import status

from backend.common.responce.messages import Msg


@dataclass
class AuthMessages:
    JWT_EXPIRED = Msg(_l("JWT_EXPIRED"), status.HTTP_401_UNAUTHORIZED)
    JWT_INVALID = Msg(_l("JWT_INVALID"), status.HTTP_401_UNAUTHORIZED)
    JWT_SESSION_EXPIRED = Msg(_l("JWT_SESSION_EXPIRED"), status.HTTP_401_UNAUTHORIZED)
    JWT_WRONG_TYPE = Msg(_l("JWT_WRONG_TYPE"), status.HTTP_401_UNAUTHORIZED)

    USER_NOT_FOUND = Msg(_l("USER_NOT_FOUND"), status.HTTP_401_UNAUTHORIZED)
    USER_INACTIVE = Msg(_l("USER_INACTIVE"), status.HTTP_403_FORBIDDEN)
    USER_NOT_VERIFIED = Msg(_l("USER_NOT_VERIFIED"), status.HTTP_403_FORBIDDEN)
    USER_NOT_SUPERUSER = Msg(_l("USER_NOT_SUPERUSER"), status.HTTP_403_FORBIDDEN)
