from app.configs.celery import celery
from app.schemas.rag.text_spliter import SplitTextArgs
from app.services.rag.store_data import save_vectorstore
from app.services.rag.text_splitter import split_text
from app.utils.logger import get_logger
from app.schemas.input.yt import TaskInput

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_save_vector_store(self, data: dict) -> dict:
    data = TaskInput(**data)
    logger.debug("Started the task of storing the data in vector store")
    try:
        text_split = SplitTextArgs(
            chat_id=data.chat_id, user_id=data.user_id, text=data.text
        )
        splited_text = split_text(data=text_split)
        save_vectorstore(chunks=splited_text)
        return data.model_dump()
    except Exception as e:
        logger.debug(
            f"Error while processing Celery task(save_vector_store): {e}",
            exc_info=True,
        )
        raise self.retry(exc=e)
