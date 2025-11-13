from app.configs.celery import celery
from app.services.common.model import get_response
from app.utils.logger import get_logger
from app.schemas.input.yt import TaskInput

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_generate_summary(self, data: dict):
    data = TaskInput(**data)
    logger.debug("Started the task of summary generation")

    try:
        summary_text = get_response(query=data.text)
        if not summary_text:
            raise ValueError("Failed to generate summary text")

        data["summary_text"] = summary_text
        return data.dict()

    except Exception as e:
        logger.debug(
            f"Error while processing Celery task(summary_generation): {e}",
            exc_info=True,
        )
        raise self.retry(exec=e)
