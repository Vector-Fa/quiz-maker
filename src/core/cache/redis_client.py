from redis.asyncio import ConnectionPool
from redis.asyncio.client import Redis

from ..config import settings

redis_connection_pool = ConnectionPool.from_url(settings.REDIS_URL, max_connections=100)


class RedisClient:
    def __init__(self):
        self.redis = Redis(connection_pool=redis_connection_pool)

    async def set(self, key, value, expire: int | None = None):
        print(value)
        result = await self.redis.set(key, value, expire)
        return result

    async def get(self, key):
        result = await self.redis.get(key)
        return result

    async def delete(self, *keys):
        return await self.redis.delete(*keys)


async def get_redis() -> RedisClient:
    return RedisClient()
