# app/core/rate_limiter.py
from fastapi import Request, HTTPException, status, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)
redis_client: Redis | None = None


async def init_rate_limiter():
    """Initialize Redis and rate limiter on startup."""
    global redis_client
    try:
        redis_url = f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/2"
        redis_client = Redis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
        await redis_client.ping()
        await FastAPILimiter.init(redis_client)
        logger.info("✅ Rate limiter initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize rate limiter: {e}")
        raise


async def close_rate_limiter():
    """Close Redis connection on shutdown."""
    global redis_client
    if redis_client:
        await FastAPILimiter.close()
        await redis_client.close()
        logger.info("Rate limiter closed")


async def get_identifier(request: Request) -> str:  # ← ADD async HERE
    """Get client identifier (IP address)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


async def rate_limit_callback(request: Request, response, pexpire: int):
    """Called when rate limit is exceeded."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Try again in {pexpire / 1000:.0f} seconds.",
        },
    )


def rate_limit_default():
    """Default rate limit: 100 requests per 60 seconds."""
    return Depends(
        RateLimiter(
            times=config.RATE_LIMIT_TIMES,
            seconds=config.RATE_LIMIT_SECONDS,
            callback=rate_limit_callback,
            identifier=get_identifier,
        )
    )


def rate_limit_custom(times: int, seconds: int):
    """Custom rate limit with specific parameters."""
    return Depends(
        RateLimiter(
            times=times,
            seconds=seconds,
            callback=rate_limit_callback,
            identifier=get_identifier,
        )
    )