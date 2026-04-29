from dataclasses import dataclass

from fastapi_babel import lazy_gettext as _l
from starlette import status

from backend.common.responce.messages import Msg


@dataclass
class AuthMessages:
    EMAIL_ALREADY_EXISTS = Msg(_l("EMAIL_ALREADY_EXISTS"), status.HTTP_409_CONFLICT)
    INVALID_CREDENTIALS = Msg(_l("INVALID_CREDENTIALS"), status.HTTP_401_UNAUTHORIZED)
    USER_NOT_FOUND = Msg(_l("USER_NOT_FOUND"), status.HTTP_401_UNAUTHORIZED)
    JWT_INVALID = Msg(_l("JWT_INVALID"), status.HTTP_401_UNAUTHORIZED)
