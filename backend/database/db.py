from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.common.models import MappedBase
from backend.core.config import settings


def create_database_async_engine(
    url: str | URL,
) -> AsyncEngine:
    return create_async_engine(
        url,
        echo=settings.db.database_echo,
        echo_pool=settings.db.database_pool_echo,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        pool_use_lifo=False,
    )


def create_database_async_session(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession | Any]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_db_sessionmaker() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    async with async_db_sessionmaker.begin() as session:
        yield session


async def create_tables() -> None:
    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all)


async def drop_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)


async def close_db() -> None:
    await async_engine.dispose()


async_engine = create_database_async_engine(str(settings.db.url))
async_db_sessionmaker = create_database_async_session(async_engine)


CurrentSession = Annotated[AsyncSession, Depends(get_db)]
CurrentSessionTransaction = Annotated[AsyncSession, Depends(get_db_transaction)]
