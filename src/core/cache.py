import json
import logging
from datetime import timedelta
from typing import Any

import redis.asyncio as aioredis

from src.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self) -> None:
        self.redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        try:
            self.redis = await aioredis.from_url(  # type: ignore[no-untyped-call]
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3,
                socket_keepalive=True,
                health_check_interval=30,
            )
            _ = await self.redis.ping()  # type: ignore[misc]
            logger.info("Redis connection established")
        except Exception:
            logger.warning("Redis unavailable — caching disabled")
            self.redis = None

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.aclose()
            self.redis = None

    @property
    def available(self) -> bool:
        return self.redis is not None

    async def _ensure_connection(self) -> bool:
        if self.redis is None:
            return False
        try:
            _ = await self.redis.ping()  # type: ignore[misc]
            return True
        except Exception:
            return False

    async def get(self, key: str) -> str | None:
        if not await self._ensure_connection():
            return None
        assert self.redis is not None
        return await self.redis.get(key)  # type: ignore[no-any-return]

    async def set(self, key: str, value: str, expire: timedelta | None = None) -> bool:
        if not await self._ensure_connection():
            return False
        assert self.redis is not None
        if expire:
            await self.redis.setex(key, expire, value)
        else:
            await self.redis.set(key, value)
        return True

    async def delete(self, key: str) -> bool:
        if not await self._ensure_connection():
            return False
        assert self.redis is not None
        _ = await self.redis.delete(key)
        return True

    async def get_json(self, key: str) -> Any:
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(self, key: str, value: Any, expire: timedelta | None = None) -> bool:
        return await self.set(key, json.dumps(value, default=str), expire)

    async def delete_pattern(self, pattern: str) -> None:
        if not await self._ensure_connection():
            return
        assert self.redis is not None
        keys: list[str] = await self.redis.keys(pattern)
        if keys:
            _ = await self.redis.delete(*keys)


cache_service = CacheService()
