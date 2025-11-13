from app.configs.celery import celery
from app.schemas.db.docs import UpdateDocsData
from app.schemas.db.message import UpdateMessage
from app.services.db.docs import update_docs
from app.services.db.message import update_message
from app.utils.logger import get_logger
from app.configs.database import engine
from sqlmodel import Session

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_update_db(self, data=dict):
    session = Session(engine)
    data = UpdateDocsData(**data)
    logger.debug("Starting the task of saving audio and summary in the db")

    try:
        question_id = data.question_id
        if not question_id:
            save_summary_and_audio = UpdateDocsData(
                user_id=data.user_id,
                chat_id=data.chat_id,
                summary_text=data.summary_text,
                audio_url=data.audio_url,
            )
            update_docs(details=save_summary_and_audio, session=session)
        else:
            save_answer_audio = UpdateMessage(
                user_id=data.user_id,
                chat_id=data.chat_id,
                question_id=question_id,
                audio_url=data.audio_url,
                content=data.summary_text,
            )
            update_message(session=session,details=save_answer_audio)

        return {"status": "completed", **data}
    except Exception as e:
        session.rollback()
        logger.debug(
            f"Error while processing Celery task(update_db_summary_audio): {e}",
            exc_info=True,
        )
        raise self.retry(exec=e)
    finally:
        session.close()
