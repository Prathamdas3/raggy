from app.configs.celery import celery
from app.utils.logger import get_logger
from app.schemas.db.docs import CreateText
from app.schemas.input.yt import TaskInput
from app.services.db.docs import save_original_text
from app.configs.database import engine
from sqlmodel import Session

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_save_original_text(self, data: dict)->dict:
    data = TaskInput(**data)
    session = Session(engine)
    logger.debug("starting to store the text in the db")

    try:
        save_text = CreateText(
            user_id=data.user_id, chat_id=data.chat_id, original_text=data.text
        )
        doc_id=save_original_text(data=save_text, session=session)
        if not doc_id:
            raise ValueError("No doc_id recived")
        logger.info(f"successfully stored the data for the docs with the id: {doc_id}")
        return data.model_dump()
    except Exception as e:
        session.rollback()
        logger.debug(
            f"Error while processing Celery task(save_original_text): {e}",
            exc_info=True,
        )
        raise self.retry(exc=e)
    finally:
        session.close()
