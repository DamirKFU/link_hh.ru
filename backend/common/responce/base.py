from typing import Any

from msgspec import json
from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.encode(content)
