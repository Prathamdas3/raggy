from celery import chain
from app.tasks.task_extract_text import task_extract_text, ExtractedDictType
from app.tasks.task_summary import (
    task_parallel_save_and_create_summary,
    task_handle_ai_generated_content,
)
from app.tasks.task_ai import task_generate_summary_and_title
from app.core import get_logger

logger = get_logger(__name__)


def chain_summary(data: ExtractedDictType):
    try:
        logger.info("✅ summary flow initiated")
        workflow = chain(
            task_extract_text.s(data),
            task_parallel_save_and_create_summary.s(),
            task_generate_summary_and_title.s(),
            task_handle_ai_generated_content.s(),
        )
        workflow.delay()
        logger.info("✅ successfully summary flow completed")
    except Exception as e:
        logger.error(
            f"Failed to start chain_input workflow: {e}",
        )
        # Optionally raise or return response for API usage
        raise
