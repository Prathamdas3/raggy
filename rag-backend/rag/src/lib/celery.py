from celery import Celery

celery = Celery(
    "input_files_extraction",
    broker="redis://localhost:6379/2",
    backend="redis://localhost:6379/3",
)


celery.autodiscover_tasks(
    [
        "workers.audio",
        "workers.answer_audio",
        "workers.db.store_summary",
        "workers.db.store_audio",
        "workers.db.store_answer",
        "workers.db.store_answer_audio",
        "workers.query",
        "workers.summary",
        "workers.upload_audio_minio",
        "workers.upload_answer_audio_to_minio",
        "workers.vectors.set_data",
    ]
)
