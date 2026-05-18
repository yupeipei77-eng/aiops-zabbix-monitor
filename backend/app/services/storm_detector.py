import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StormDetector:
    def __init__(self, redis_client: aioredis.Redis | None = None):
        self._redis: aioredis.Redis | None = redis_client

    async def _get_redis(self):
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def check_and_record(self) -> bool:
        redis = await self._get_redis()
        key = "aiops:storm:counter"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, settings.STORM_WINDOW_SECONDS)
        is_storm = count > settings.STORM_THRESHOLD
        if is_storm:
            logger.warning("Storm detected: %d alerts in window", count)
        return is_storm

    async def get_current_count(self) -> int:
        redis = await self._get_redis()
        val = await redis.get("aiops:storm:counter")
        return int(val) if val else 0

    async def close(self) -> None:
        if self._redis and hasattr(self._redis, "close"):
            await self._redis.close()
