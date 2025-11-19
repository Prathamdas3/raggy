from celery import Celery
from app.config import config

celery = Celery(
    "new_api",
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/0",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/1",
    include=[
        "app.tasks.input",
        "app.tasks.pipeline",
        "app.tasks.chains",
        "app.tasks.rag",
    ],
)
