from celery import Celery

celery = Celery(
    "new_api",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=[
        "app.tasks.input",
        "app.tasks.pipeline",
        "app.tasks.chains",
    ],
)
