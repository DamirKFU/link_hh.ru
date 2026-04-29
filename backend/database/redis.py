# database/redis.py

import sys
from enum import StrEnum
from typing import Annotated, Awaitable, Callable

from fastapi import Depends
from redis.asyncio import Redis
from redis.exceptions import AuthenticationError
from redis.exceptions import TimeoutError as RedisTimeoutError

from backend.common.logging import log
from backend.common.resources import strings
from backend.core.config import settings


class RedisDB(StrEnum):
    CACHE = settings.redis.cache_db
    AUTH = settings.redis.auth_db


class RedisCli(Redis):
    def __init__(
        self,
        host: str = settings.redis.host,
        port: int = settings.redis.port,
        password: str = settings.redis.password.get_secret_value(),
        db: str = RedisDB.CACHE,
        socket_timeout: int = settings.redis.timeout,
        socket_connect_timeout: int = settings.redis.timeout,
        socket_keepalive: bool = True,
        health_check_interval: int = 30,
        decode_responses: bool = True,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            password=password,
            db=db,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            socket_keepalive=socket_keepalive,
            health_check_interval=health_check_interval,
            decode_responses=decode_responses,
        )

    async def init(self) -> None:
        try:
            result = self.ping()
            if not isinstance(result, bool):
                await result

            log.debug(
                strings.REDIS_CONNECTED,
                self.connection_pool.connection_kwargs.get("db"),
            )
        except RedisTimeoutError:
            log.error(strings.REDIS_TIMEOUT)
            sys.exit()
        except AuthenticationError:
            log.error(strings.REDIS_AUTH_ERROR)
            sys.exit()
        except Exception as e:
            log.error(strings.REDIS_UNKNOWN_ERROR, e)
            sys.exit()


class RedisCliFactory:
    _instances: dict[str, RedisCli] = {}

    @classmethod
    async def get_redis(cls, db: str = RedisDB.CACHE) -> RedisCli:
        if db not in cls._instances:
            client = RedisCli(db=db)
            await client.init()
            cls._instances[db] = client
        return cls._instances[db]

    @classmethod
    async def close_all(cls) -> None:
        for client in cls._instances.values():
            await client.aclose()
            log.debug(
                strings.REDIS_CLOSED,
                client.connection_pool.connection_kwargs.get("db"),
            )
        cls._instances.clear()

    @classmethod
    async def init_all(cls) -> None:
        for db in RedisDB:
            await cls.get_redis(db)

    @classmethod
    async def get_all(cls) -> list[RedisCli]:
        return list(cls._instances.values())


def get_redis_dep(db: RedisDB) -> Callable[[], Awaitable[RedisCli]]:
    async def _get_redis() -> RedisCli:
        return await RedisCliFactory.get_redis(db=db)

    return _get_redis


AuthRedis = Annotated[RedisCli, Depends(get_redis_dep(RedisDB.AUTH))]
CacheRedis = Annotated[RedisCli, Depends(get_redis_dep(RedisDB.CACHE))]
