from celery import Celery

celery = Celery(
    "input_files_extraction",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)


celery.autodiscover_tasks(
    [
        "workers.documents",
        "workers.audio_video",
        "workers.images",
        "workers.yt",
        "workers.text_splitter",
        "workers.db.store_text_worker",
        "workers.db.summary_generate",
        "workers.db.store_vector_storage",
    ]
)
