from configs.celery import celery
from utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("staring workers......")
    celery.start(
        argv=[
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "-E",  # Optional: set task routes, time limits, etc.
        ]
    )
