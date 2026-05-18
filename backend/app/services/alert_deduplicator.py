import json
from datetime import datetime, timezone

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertDeduplicator:
    def __init__(self, redis_client: aioredis.Redis | None = None):
        self._redis: aioredis.Redis | None = redis_client

    async def _get_redis(self):
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def check_and_record(self, dedup_key: str) -> tuple[bool, int]:
        redis = await self._get_redis()
        key = f"aiops:dedup:{dedup_key}"
        now = datetime.now(timezone.utc).isoformat()
        existing = await redis.get(key)
        if not existing:
            value = {"count": 1, "first_seen": now, "last_seen": now}
            await redis.set(key, json.dumps(value), ex=settings.DEDUP_WINDOW_SECONDS)
            return False, 1

        try:
            value = json.loads(existing)
        except (TypeError, ValueError):
            value = {"count": int(existing), "first_seen": now}

        value["count"] = int(value.get("count", 0)) + 1
        value.setdefault("first_seen", now)
        value["last_seen"] = now
        await redis.set(key, json.dumps(value), ex=settings.DEDUP_WINDOW_SECONDS)
        return True, value["count"]

    async def get_dedup_count(self, dedup_key: str) -> int:
        redis = await self._get_redis()
        key = f"aiops:dedup:{dedup_key}"
        val = await redis.get(key)
        if not val:
            return 0
        try:
            data = json.loads(val)
            return int(data.get("count", 0))
        except (TypeError, ValueError):
            return int(val)

    async def close(self) -> None:
        if self._redis and hasattr(self._redis, "close"):
            await self._redis.close()
