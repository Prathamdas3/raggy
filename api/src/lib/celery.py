from celery import Celery

celery = Celery(
    "input_files_extraction",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)


celery.autodiscover_tasks(
    [
        "workers.input.documents",
        "workers.input.audio_video",
        "workers.input.images",
        "workers.input.yt",
        "workers.input.text_splitter",
        "workers.db.store_text_worker",
        "workers.db.summary_generate",
        "workers.db.store_vector_storage",
        "workers.db.store_summary",
        "workers.db.store_audio",
        "workers.db.store_answer",
        "workers.db.store_answer_audio",
        "workers.rag.audio",
        "workers.rag.answer_audio",
        "workers.rag.query",
        "workers.rag.summary",
        "workers.rag.upload_audio_minio",
        "workers.rag.upload_answer_audio_to_minio",
        "workers.rag.set_data",
    ]
)
