from app.schemas.input.file import OtherInput
from app.schemas.input.yt import TaskInput
from app.services.input.other import handle_other_file
from app.utils.logger import get_logger
from app.configs.celery import celery

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_other_files_text(self, data: dict):
    data = OtherInput(**data)
    logger.debug(
        "Starting my text extraction task form other files like pdf, doc, text ...."
    )

    if not data.sub_type:
        raise ValueError("Sub type is missing....")

    try:
        text = handle_other_file(file_path=data.path, file_type=data.sub_type)

        if not text or not text.strip():
            raise ValueError(f"{data.sub_type} to text conversion failed")

        save_text_db = TaskInput(chat_id=data.chat_id, user_id=data.user_id, text=text)
        return save_text_db.model_dump()

    except Exception as e:
        logger.error(
            f"Error while processing Celery task(other_files_text): {str(e)}",
            exc_info=True,
        )

        raise self.retry(exc=e)
