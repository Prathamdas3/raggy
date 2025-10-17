from utils.celery import celery
from utils.logger import get_logger

logger = get_logger("worker")

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    celery.start( argv=[
            'worker',
            '--loglevel=info',
            '--concurrency=4',
            '-E'
            # Optional: set task routes, time limits, etc.
        ])