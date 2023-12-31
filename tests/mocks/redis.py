class MockRedis:
    redis = dict()

    async def set(self, key, value, expire: int | None = None):
        self.redis[key] = value
        return True

    async def get(self, key):
        return self.redis.get(key)

    async def delete(self, key):
        del self.redis[key]

    async def exists(self, key):
        if self.redis.get(key):
            return 1
        return 0
