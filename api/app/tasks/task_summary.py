from uuid import UUID

from app.tasks.task_save_text import task_save_original_text_vector_db
from app.tasks.task_generate_audio import task_generate_audio
from app.core import get_logger, celery
from app.models import UpdateChat, UpdateSummary

from celery import chain
from typing import TypedDict

logger = get_logger(__name__)


class CreateSummaryReturn(TypedDict):
    summary_id: str
    content: str
    chat_id: str


@celery.task(
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    name="task_update_summary",
)
def task_update_summary(self, data: dict):
    """
    Works for both cases:
    - updating content:   {"summary_id": "...", "content": "..."}
    - updating audio_url: {"summary_id": "...", "audio_url": "..."}
    - updating both:      {"summary_id": "...", "content": "...", "audio_url": "..."}
    """

    id = data.get("summary_id")
    if not isinstance(id, str) or not id.strip():
        raise ValueError("Invalid summary id")

    try:
        from app.db import get_celery_session
        from app.services import get_summary_service

        with get_celery_session() as session:
            service = get_summary_service(session=session)
            details = UpdateSummary(
                audio_url=data.get("audio_url"),
                summary_id=id,
                content=data.get("content"),
            )
            service.update_summary(data=details)
            logger.info("✅ successfully updated the summary")
        return data
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_update_title",
)
def task_update_title(self, data: dict):
    title = data.get("title")
    chat_id = data.get("chat_id")
    if not isinstance(title, str) or not title.strip():
        return
    if not isinstance(chat_id, str) or not chat_id.strip():
        raise ValueError("Invalid chat id to update the title")

    try:
        from app.db import get_celery_session
        from app.services import get_chat_service

        with get_celery_session() as session:
            service = get_chat_service(session=session)
            details = UpdateChat(chat_id=chat_id, title=title)
            service.update_chat(details=details)
            logger.info("✅ successfully updated the title")
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_parallel_save_and_create_summary",
)
def task_parallel_save_and_create_summary(self, data: dict) -> dict:
    try:
        # fire and forget — doesn't affect the chain
        task_save_original_text_vector_db.delay(data)

        # create summary and return result to next chain task
        from app.db import get_celery_session
        from app.services import get_summary_service

        with get_celery_session() as session:
            service = get_summary_service(session=session)
            summary_id = service.create_summary(chat_id=UUID(data.get("chat_id")))

        return {
            **data,
            "summary_id": str(summary_id),
        }
    except Exception as e:
        logger.error(f"Failed to process parallel tasks: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_handle_ai_generated_content",
)
def task_handle_ai_generated_content(self, data: dict):
    try:
        chain(
            # task_update_summary.s(data),
            task_generate_audio.s(data),
            task_update_summary.s(),
            task_update_title.s(),
        ).delay()

    except Exception as e:
        logger.error("Failed to handle the ai generated content")
        raise self.retry(exc=e)
