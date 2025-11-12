from app.configs.celery import Celery
from app.schemas.db.docs import CreateText
from app.schemas.input.yt import SpechInput, TaskInput
from app.schemas.rag.text_spliter import SplitTextArgs
from app.services.common.model import get_response
from app.services.db.docs import save_original_text
from app.services.rag.store_data import save_vectorstore
from app.services.rag.text_splitter import split_text
from app.tasks.core.spech_text_save import task_spech_text_save
from app.utils.logger import get_logger
from app.configs.database import Session,engine

logger = get_logger(__name__)


@Celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_save_text_db(self, data: TaskInput):
    logger.debug("starting to store the text ")

    try:
        save_text = CreateText(
            user_id=data.user_id, chat_id=data.chat_id, original_text=data.text
        )
        save_original_text(data=save_text)

        text_split = SplitTextArgs(
            chat_id=data.chat_id, user_id=data.user_id, text=data.text
        )
        splited_text = split_text(data=text_split)
        save_vectorstore(chunks=splited_text)

        summary_text = get_response(query=save_text)
        if not summary_text:
            raise ValueError("Failed to generate summary text")

        summary_data = SpechInput(
            user_id=data.user_id, chat_id=data.chat_id, summary_text=summary_text
        )
        task_spech_text_save.delay(data=summary_data)
    except Exception:
        raise
