from celery import Celery

celery = Celery(
    "input_files_extraction",
    broker="redis://localhost:6379/2",
    backend="redis://localhost:6379/3",
)


celery.autodiscover_tasks(
    [
        "workers.summary",
        "workers.db.store_summary",
        "workers.db.store_audio",
        "workers.upload_audio_minio",
        "workers.audio"
    ]
)
