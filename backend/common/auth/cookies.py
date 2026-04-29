from typing import Annotated, Callable, Optional

from fastapi import Cookie, Depends

from backend.common.auth.messages import AuthMessages
from backend.common.exceptions.errors import ApiHTTPException
from backend.core.config import settings


def get_cookie_dep(
    cookie_name: str, required: bool = True
) -> Callable[[Optional[str]], Optional[str]]:
    def _get_cookie(
        value: Annotated[
            Optional[str],
            Cookie(alias=cookie_name),
        ] = None,
    ) -> Optional[str]:
        if required and value is None:
            raise ApiHTTPException(AuthMessages.JWT_INVALID)
        return value

    return _get_cookie


AccessToken = Annotated[
    str,
    Depends(get_cookie_dep(settings.auth.access_cookie_name)),
]
RefreshToken = Annotated[
    str,
    Depends(get_cookie_dep(settings.auth.refresh_cookie_name)),
]
OptionalRefreshToken = Annotated[
    Optional[str],
    Depends(get_cookie_dep(settings.auth.refresh_cookie_name, required=False)),
]
