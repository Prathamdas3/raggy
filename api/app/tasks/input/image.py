from app.configs.celery import celery
from app.schemas.input.file import OtherInput
from app.schemas.input.yt import TaskInput
from app.services.input.image_text import png_to_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_png_text(self, data: dict):
    data = OtherInput(**data)
    logger.debug("starting the task to convert the audio or video into text")

    try:
        text = png_to_text(path=data.path)

        if not text or not text.strip():
            raise ValueError("Png to text conversion failed")

        save_text_db = TaskInput(chat_id=data.chat_id, user_id=data.user_id, text=text)
        return save_text_db.model_dump()

    except Exception as e:
        logger.error(
            f"Error while processing Celery task(png_text): {str(e)}",
            exc_info=True,
        )

        raise self.retry(exc=e)
