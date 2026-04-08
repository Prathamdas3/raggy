import redis.asyncio as aioredis
import redis
from app.core.config import config

async_redis_client = aioredis.from_url(f"redis://{config.redis_host}:{config.redis_port}", decode_responses=True)
sync_redis_client = redis.from_url(f"redis://{config.redis_host}:{config.redis_port}", decode_responses=True)