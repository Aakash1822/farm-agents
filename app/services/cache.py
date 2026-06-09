import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

class CacheService:
    """Redis cache wrapper (optional, works without Redis)"""
    
    def __init__(self):
        self.redis = None
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        if not self.redis:
            return
        await self.redis.setex(key, ttl, json.dumps(value))

cache = CacheService()