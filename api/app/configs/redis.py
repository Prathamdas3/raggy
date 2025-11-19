from redis.asyncio import Redis
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Get Redis connection."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client


async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = Redis.from_url(
            config.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            password=config.REDIS_PASSWORD
        )
        # Test connection
        await redis_client.ping()
        logger.info(f"✅ Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        raise


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")