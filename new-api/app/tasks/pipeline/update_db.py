from app.configs.celery import celery
from app.schemas.db.docs import UpdateDocsData
from app.schemas.db.message import UpdateMessage
from app.services.db.docs import update_docs
from app.services.db.message import update_message
from app.utils.logger import get_logger
from app.configs.database import get_celery_session


logger = get_logger(__name__)

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_update_db(self, data: dict) -> dict:
    """
    Updates either docs (summary + audio) or message (answer audio).
    Uses context manager for automatic commit/rollback.
    """
    try:
        data = UpdateDocsData(**data)
        logger.debug(f"Starting task_update_db for user_id={data.user_id}, chat_id={data.chat_id}")
        
        with get_celery_session() as session:
            question_id = data.question_id
            
            if not question_id:
                # Update docs table with summary and audio
                logger.debug("Updating docs with summary and audio")
                save_summary_and_audio = UpdateDocsData(
                    user_id=data.user_id,
                    chat_id=data.chat_id,
                    summary_text=data.summary_text,
                    audio_url=data.audio_url,
                )
                update_docs(details=save_summary_and_audio, session=session)
                logger.info(f"Successfully updated docs for chat_id={data.chat_id}")
                
            else:
                # Update message table with answer audio
                logger.debug(f"Updating message with answer audio for question_id={question_id}")
                save_answer_audio = UpdateMessage(
                    user_id=data.user_id,
                    chat_id=data.chat_id,
                    question_id=question_id,
                    audio_url=data.audio_url,
                    content=data.summary_text,
                )
                update_message(session=session, details=save_answer_audio)
                logger.info(f"Successfully updated message for question_id={question_id}")
            
            # Context manager auto-commits here if no exception
            return {"status": "completed", **data.model_dump()}
            
    except Exception as e:
        # Context manager auto-rollbacks on exception
        logger.error(f"Error in task_update_db: {e}", exc_info=True)
        raise self.retry(exc=e)