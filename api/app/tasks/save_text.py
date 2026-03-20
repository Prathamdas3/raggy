"""Celery tasks for saving text content.

Contains background tasks for saving chat text to database and vector store.
"""

from uuid import UUID
from app.core import celery, get_logger, qdrant_store
from app.db import get_celery_session
from app.services import get_chat_service, UpdateChat
from typing import TypedDict

logger = get_logger(__name__)


class SaveArgs(TypedDict):
    """Type definition for save task arguments.

    Attributes:
        chat_id: UUID string of the chat.
        title: Chat title.
        content: Text content to save.
    """

    chat_id: str
    title: str
    content: str


@celery.task(
    bind=True, max_retries=3, default_retry_delay=10, name="task_save_original_text_db"
)
def task_save_original_text_db(self, data: SaveArgs) -> SaveArgs:
    """Save extracted text content to the database.

    Updates the chat with the extracted title and original text content.

    Args:
        data: SaveArgs containing chat_id, title, and content.

    Returns:
        The original data dict.

    Retries:
        Automatically retries up to 3 times on failure.
    """
    try:
        with get_celery_session() as session:
            chat = get_chat_service(session=session)
            details = UpdateChat(
                title=data.get("title"), original_text=data.get("content")
            )
            chat.update_chat(chat_id=UUID(data.get("chat_id")), details=details)
        return data
    except Exception as e:
        logger.error(f"Failed to save the text in the db: {str(e)}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_save_original_text_vector_db",
)
def task_save_original_text_vector_db(self, data: SaveArgs) -> SaveArgs:
    """Save text content to the vector database.

    Embeds and stores the text content in Qdrant for similarity search.

    Args:
        data: SaveArgs containing chat_id, title, and content.

    Returns:
        The original data dict.

    Retries:
        Automatically retries up to 3 times on failure.
    """
    try:
        from app.utils import text_split

        content = text_split(text=data.get("content"))
        qdrant_store.save(
            texts=content.texts, metadatas=content.metadatas, ids=content.ids
        )
        return data
    except Exception as e:
        logger.error(f"Failed to store the original text in the vector db: {str(e)}")
        raise self.retry(exc=e)
