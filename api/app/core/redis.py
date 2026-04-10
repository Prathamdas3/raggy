from app.core.config import config
from redis import Redis
import redis

redis_client:Redis=redis.from_url(f"redis://{config.redis_host}:{config.redis_port}", decode_responses=True)