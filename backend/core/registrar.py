from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi_babel import BabelMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import ContextMiddleware

from backend import __version__
from backend.apps.router import router
from backend.common.babel import babel_config
from backend.common.exceptions.exception_handlers import register_exception_handlers
from backend.common.logging import setup_logging
from backend.common.telemetry import init_otel
from backend.core.config import settings
from backend.database.db import (
    close_db,
    create_tables,
)
from backend.database.redis import RedisCliFactory
from backend.middlewares.csrf import CustomCSRFMiddleware
from backend.utils.trace_id import OtelTraceIdPlugin


@asynccontextmanager
async def register_init(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    await create_tables()
    await RedisCliFactory.init_all()

    yield

    await close_db()
    await RedisCliFactory.close_all()


def register_app() -> FastAPI:
    app = FastAPI(
        title=settings.api.title,
        version=__version__,
        description=settings.api.description,
        docs_url=settings.api.docs_url,
        redoc_url=settings.api.redoc_url,
        openapi_url=settings.api.openapi_url,
        # default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    register_logger()
    register_router(app)
    init_otel(app)
    register_middleware(app)

    register_exception_handlers(app)

    return app


def register_logger() -> None:
    setup_logging()


def register_router(app: FastAPI) -> None:
    app.include_router(router)


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.core.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        CustomCSRFMiddleware,
        secret=settings.core.secret_key.get_secret_value(),
        exempt_urls=settings.csrf.compiled_exempt_urls,
        cookie_secure=settings.csrf.cookie_secure,
        cookie_samesite=settings.csrf.cookie_samesite,
    )

    app.add_middleware(
        ContextMiddleware,
        plugins=[OtelTraceIdPlugin()],
    )
    app.add_middleware(
        BabelMiddleware,
        babel_configs=babel_config,
    )
