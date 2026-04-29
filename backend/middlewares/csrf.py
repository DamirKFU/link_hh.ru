from fastapi import Request, Response
from starlette_csrf.middleware import CSRFMiddleware

from backend.common.responce.helpers import error
from backend.common.responce.messages import MessagesBase


class CustomCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> Response:
        return error(
            msg=MessagesBase.CSRF_FORBIDDEN,
        )
