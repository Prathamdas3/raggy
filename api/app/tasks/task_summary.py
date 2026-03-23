from uuid import UUID

from app.tasks.task_save_text import task_save_original_text_vector_db, SaveArgs
from app.tasks.task_generate_audio import task_generate_audio
from app.core import get_logger, celery, ai_model
from app.constants import MODEL_PROMPT_SUMMARY
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils import parse_title_and_summary
from app.models import UpdateChat, UpdateSummary

from celery import group, chain
from typing import TypedDict

logger = get_logger(__name__)


class CreateSummaryReturn(TypedDict):
    summary_id: str
    content: str
    chat_id: str


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_create_summary",
)
def task_create_summary(self, data: SaveArgs) -> CreateSummaryReturn:
    try:
        from app.db import get_celery_session, VariantType
        from app.services import get_summary_service

        with get_celery_session() as session:
            summary = get_summary_service(session=session)
            summary_id = summary.create_summary(
                chat_id=UUID(data.get("chat_id")), variant_type=VariantType.default
            )
            return_value: CreateSummaryReturn = {
                "summary_id": str(summary_id),
                "content": data.get("content"),
                "chat_id": data.get("chat_id"),
            }
            return return_value
    except Exception as e:
        logger.error(f"Failed to store the original text in the vector db: {str(e)}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
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
    try:
        from app.db import get_celery_session
        from app.services import get_summary_service

        with get_celery_session() as session:
            service = get_summary_service(session=session)
            details = UpdateSummary(
                audio_url=data.get("audio_url"),
                summary_id=UUID(data.get("summary_id")),
                content=data.get("content"),
            )
            service.update_summary(data=details)
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
    try:
        from app.db import get_celery_session
        from app.services import get_chat_service

        chat_id = data.get("chat_id")
        title = data.get("title")
        if title is not None:
            with get_celery_session() as session:
                service = get_chat_service(session=session)
                details = UpdateChat(chat_id=UUID(chat_id), title=title)
                return service.update_chat(details=details)
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_update_summary",
)
def task_generate_summary_and_title(self, data: CreateSummaryReturn) -> dict[str, str]:
    try:
        messages = [
            SystemMessage(content=MODEL_PROMPT_SUMMARY),
            HumanMessage(content=data.get("content")),
        ]
        response = ai_model.invoke(messages=messages)

        if not response.content:
            raise ValueError("Model returned empty response.")

    except Exception as e:
        logger.error(f"Failed to generate the summary: {str(e)}")
        raise self.retry(exc=e)

    try:
        content = response.content
        content_str = str(content).strip() if content else ""
        if not content_str:
            logger.error("Model returned empty content")
            raise RuntimeError(
                "Model generated empty response. Check prompt formatting and model configuration."
            )
        title, summary = parse_title_and_summary(content=content_str)
        return_value = {
            "summary_id": data.get("summary_id"),
            "chat_id": data.get("chat_id"),
            "content": summary,
            "title": title,
        }
        return return_value
    except ValueError as e:
        logger.error(
            f"Failed to parse model response: {e}. Response was: {response.content[:200]}"
        )
        raise


@celery.task(
    max_retries=3,
    default_retry_delay=10,
    name="task_parallel_save_and_create_summary",
    bind=True,
)
def task_parallel_save_and_create_summary(self, data: SaveArgs):
    try:
        group(task_save_original_text_vector_db.s(data), task_create_summary.s(data)).delay()
    except Exception as e:
        logger.error(f"Failed to process the parallel tasks: {str(e)}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_handle_ai_generated_content",
)
def task_handle_ai_generated_content(self, data: dict):
    try:
        group(
            task_update_summary.s(data),
            task_update_title.s(data),
            chain(task_generate_audio.s(data), task_update_summary.s()),
        ).delay()
    except Exception as e:
        logger.error("Failed to handle the ai generated content")
        raise self.retry(exc=e)
