import aioredis
from aioredis import Redis


class RedisService:
    def __init__(self, connect_url: str):
        self._redis: Redis = aioredis.from_url(url=connect_url)

    async def get(self, key: str):
        return await self._redis.get(name=key)

    async def set(self, key: str, value: str, expire: int):
        return await self._redis.set(name=key, value=value, ex=expire)

    async def remove(self, key: str):
        return await self._redis.delete(key)

    async def close(self):
        await self._redis.close()
