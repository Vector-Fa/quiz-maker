class MockRedis:
    redis = dict()

    async def set(self, key, value, expire: int | None = None):
        self.redis[key] = value
        return True

    async def get(self, key):
        return self.redis[key]