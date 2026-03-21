"""Celery tasks for text extraction.

Contains background tasks for extracting text content from files.
"""

from app.core import celery, get_logger
from app.models import ExtractChat
from app.utils import extract_pdf_content
from typing import TypedDict
from app.tasks.save_text import SaveArgs

logger = get_logger(__name__)


class ExtractedDictType(TypedDict):
    """Type definition for extraction task arguments.

    Attributes:
        doc_id: UUID string of the document/chat.
        file_path: Path to the file to extract from.
        file_type: Type of the file (e.g., 'document').
    """

    doc_id: str
    stroage_key: str
    file_type: str


@celery.task(bind=True, max_retries=3, default_retry_delay=10, name="task_extract_text")
def task_extract_text(self, data: ExtractedDictType) -> SaveArgs:
    """Extract text content from a file.

    Reads the file, extracts title and text content, and returns
    the data in a format suitable for saving.

    Args:
        data: ExtractedDictType containing doc_id, file_path, and file_type.

    Returns:
        SaveArgs with extracted title, content, and chat_id.

    Raises:
        ValueError: If no content can be extracted.

    Retries:
        Automatically retries up to 3 times on failure.
    """
    try:
        data = ExtractChat(**data).model_dump()
        content = extract_pdf_content(storage_key=data.get("stroage_key"))
        if  not content.content:
            raise ValueError("No content found from the given file path")
        return {
            "content": content.content,
            "chat_id": str(data.doc_id),
        }
    except Exception as e:
        logger.error(
            f"Failed to extract the file content of type {data.get('file_type')}:{str(e)}"
        )
        raise self.retry(exc=e)
