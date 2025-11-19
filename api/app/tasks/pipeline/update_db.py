from app.configs.celery import celery
from app.schemas.db.docs import UpdateDocsData
from app.services.db.docs import update_docs
from app.utils.logger import get_logger
from app.configs.database import get_celery_session

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_update_db(self, data: dict) -> dict:
    """Updates either docs (summary + audio) or message (answer audio)."""
    try:
        data = UpdateDocsData(**data)
        logger.debug(
            f"Starting task_update_db: chat_id={data.chat_id}, question_id={data.question_id}"
        )

        with get_celery_session() as session:
            # The update_docs function handles both cases internally
            doc_id = update_docs(session=session, details=data)

            logger.info(f"✅ Successfully updated: {doc_id}")

            # Context manager auto-commits here
            return {"status": "completed", "doc_id": str(doc_id), **data.model_dump()}

    except Exception as e:
        logger.error(f"Error in task_update_db: {e}", exc_info=True)
        raise self.retry(exc=e)
