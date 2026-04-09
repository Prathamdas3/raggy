from app.core.config import config
import redis

redis_client=redis.from_url(f"redis://{config.redis_host}:{config.redis_port}", decode_responses=True)