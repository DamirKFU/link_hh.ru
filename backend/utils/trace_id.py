from typing import Any

from opentelemetry import trace
from starlette.requests import HTTPConnection, Request
from starlette_context.plugins import Plugin

from backend.common.context import ctx
from backend.core.config import settings


def get_request_trace_id() -> str:
    if ctx.exists():
        return str(ctx.get(settings.trace_id.header, settings.trace_id.default_value))
    return settings.trace_id.default_value


class OtelTraceIdPlugin(Plugin):
    key = settings.trace_id.header

    async def process_request(self, request: Request | HTTPConnection) -> Any:
        span = trace.get_current_span()
        span_ctx = span.get_span_context()

        if span_ctx.is_valid:
            return trace.format_trace_id(span_ctx.trace_id)

        return settings.trace_id.default_value
