from redis.asyncio import Redis

from backend.common.resources import constants
from backend.core.config import settings


class RedisNamespace:
    def __init__(self, prefix: str, ttl: int) -> None:
        self.prefix = prefix
        self.ttl = ttl

    def key(self, *parts: str) -> str:
        return f"{self.prefix}:{':'.join(parts)}"

    async def set(self, redis: Redis, value: str, *parts: str) -> None:
        await redis.set(self.key(*parts), value, ex=self.ttl)

    async def get(self, redis: Redis, *parts: str) -> str | None:
        value: str | None = await redis.get(self.key(*parts))
        return value

    async def delete(self, redis: Redis, *parts: str) -> None:
        await redis.delete(self.key(*parts))


class SessionNamespace(RedisNamespace):
    async def set_used(self, redis: Redis, user_id: str, session_uuid: str) -> None:
        await redis.set(
            self.key(user_id, session_uuid),
            constants.REDIS_SESSION_USED_VALUE,
            keepttl=True,
        )

    async def delete_all(self, redis: Redis, user_id: str) -> None:
        pattern = f"{self.prefix}:{user_id}:*"
        async for key in redis.scan_iter(pattern):
            await redis.delete(key)


sessions = SessionNamespace(
    prefix=constants.SESSION_REDIS_PREFIX,
    ttl=settings.auth.refresh_token_expire_seconds,
)

reset_sessions = RedisNamespace(
    prefix=constants.PASSWORD_RESET_PREFIX,
    ttl=settings.auth.password_reset_expire_seconds,
)
