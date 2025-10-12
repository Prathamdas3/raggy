from celery import Celery

celery = Celery(
    "input_files_extraction",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
