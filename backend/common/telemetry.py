# backend/common/telemetry.py
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from backend import __version__
from backend.core.config import settings
from backend.database.db import async_engine


def init_otel(app: FastAPI) -> None:
    resource = Resource(
        attributes={
            "service.name": settings.api.title,
            "service.version": __version__,
        }
    )

    provider = TracerProvider(resource=resource)

    trace.set_tracer_provider(provider)
    AsyncioInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=async_engine.sync_engine)
    FastAPIInstrumentor.instrument_app(app)
