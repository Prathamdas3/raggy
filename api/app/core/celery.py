"""Celery configuration.

Configures Celery for background task processing using Redis as broker and backend.
"""

from celery import Celery
from app.core.config import config

celery = Celery(
    "raggy_api",
    broker=f"redis://{config.redis_host}:{config.redis_port}/0",
    backend=f"redis://{config.redis_host}:{config.redis_port}/1",
    include=["app.queues.tasks","app.queues.chains"],
)
