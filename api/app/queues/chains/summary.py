from celery import chain
from app.core import get_logger, celery
from app.queues.tasks import (
    task_generate_audio,
    task_extract_text,
    ExtractedDictType,
    task_parallel_save_and_create_summary,
    task_generate_summary_and_title,
    task_update_summary,
    task_update_title,
)

logger = get_logger(__name__)


def chain_summary(data: ExtractedDictType):
    try:
        logger.info("✅ summary flow initiated")
        workflow = chain(
            task_extract_text.s(data),
            task_parallel_save_and_create_summary.s(),
            task_generate_summary_and_title.s(),
            chain_ai_generated_content.s(),
        )
        workflow.delay()
        logger.info("✅ successfully summary flow completed")
    except Exception as e:
        logger.error(
            f"Failed to start chain_input workflow: {e}",
        )
        # Optionally raise or return response for API usage
        raise


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="chain_ai_generated_content",
)
def chain_ai_generated_content(self, data: dict):
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
