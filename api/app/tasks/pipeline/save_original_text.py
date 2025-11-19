from app.configs.celery import celery
from app.utils.logger import get_logger
from app.schemas.db.docs import CreateText
from app.schemas.input.yt import TaskInput
from app.services.db.docs import save_original_text
from app.configs.database import get_celery_session
from app.models.all_schema import User,Chats,Docs
from sqlmodel import select

logger = get_logger(__name__)



@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_save_original_text(self, data: dict) -> dict:
    data = TaskInput(**data)
    logger.debug(f"Starting task for user_id={data.user_id}, chat_id={data.chat_id}")
    
    try:
        # Use context manager - auto commits on success, auto rolls back on error
        with get_celery_session() as session:
            # Verify foreign keys exist
            user_exists = session.exec(
                select(User).where(User.id == data.user_id)
            ).first()
            
            chat_exists = session.exec(
                select(Chats).where(Chats.id == data.chat_id)
            ).first()
            
            if not user_exists:
                raise ValueError(f"User {data.user_id} does not exist")
            
            if not chat_exists:
                raise ValueError(f"Chat {data.chat_id} does not exist")
            
            # Create the document
            save_text = CreateText(
                user_id=data.user_id,
                chat_id=data.chat_id,
                original_text=data.text
            )
            
            doc_id = save_original_text(session=session, data=save_text)
            
            if not doc_id:
                raise ValueError("No doc_id received")
            
            logger.info(f"Successfully stored docs with id: {doc_id}")
            
            # Verify it was saved (still in same transaction)
            verification = session.exec(
                select(Docs).where(Docs.id == doc_id)
            ).first()
            
            if verification:
                logger.debug(f"Verified doc {doc_id}, text length: {len(verification.original_text)}")
            else:
                raise ValueError(f"Failed to verify doc {doc_id} after save")
            
            return data.model_dump()
            
    except Exception as e:
        logger.error(f"Error in task_save_original_text: {e}", exc_info=True)
        raise self.retry(exc=e)
