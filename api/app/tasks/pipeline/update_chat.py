from app.configs.database import get_celery_session
from app.schemas.db.message import UpdateMessage
from app.services.db.message import update_message
from app.utils.logger import get_logger
from app.configs.celery import celery

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_update_chat(self, data: dict) -> dict:
    """Updates answer from the chat id and question id"""
    try:
        data = UpdateMessage(**data)
        logger.debug(
            f"Starting task_update_chat: chat_id={data.chat_id}, question_id={data.question_id}"
        )

        with get_celery_session() as session:
            answer_id = update_message(details=data, session=session)
            if not answer_id:
                raise ValueError("Failed to update the answer")
            logger.info(f"Successfully updated: {answer_id}")

            return {"status": "updated", "answer_id": str(answer_id)}
    except Exception as e:
        logger.error(f"Error while updating the answer,error:{str(e)}", exc_info=True)
        raise self.retry(exc=e)
