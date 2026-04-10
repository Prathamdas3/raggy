"""Celery tasks for saving text content.

Contains background tasks for saving chat text to database and vector store.
"""

from app.core import celery, get_logger
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
    content: str


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
        data: SaveArgs containing chat_id, and content.

    Returns:
        The original data dict.

    Retries:
        Automatically retries up to 3 times on failure.
    """
    try:
        from app.utils import text_split
        from app.core import qdrant_store

        content = text_split(text=data.get("content"))
        qdrant_store.save(
            texts=content.texts, metadatas=content.metadatas, ids=content.ids
        )
        logger.info("✅ successfully saved the text in the vector db")
        return data
    except Exception as e:
        logger.error(f"Failed to store the original text in the vector db: {str(e)}")
        raise self.retry(exc=e)
