"""File upload API endpoints.

Provides endpoints for uploading and processing files including PDFs.
"""

from fastapi import APIRouter, status, UploadFile, File, HTTPException, Depends
from app.core import get_logger
from app.models import Response, FileMeta, Status
from app.utils import save_upload_to_minio
from app.services import get_chat_service, ChatService
from app.api.v1.auth import get_user_id, RefreshTokenUserId


file_router = APIRouter(prefix="/upload")
logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Only PDF files are allowed. Got: {file.content_type}",
        )
    # read and check actual size
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit.",
        )
    # reset pointer so downstream can read again
    file.file.seek(0)


@file_router.post(
    "/files", status_code=status.HTTP_202_ACCEPTED, response_model=Response
)
def upload_file(
    file: UploadFile = File(...),
    chat_services: ChatService = Depends(get_chat_service),
    user: RefreshTokenUserId = Depends(get_user_id),
):
    """Upload a file for processing.

    Saves the file to disk, creates a new chat entry, and extracts
    text content from PDF files.

    Args:
        file: The uploaded file.
        chat_services: Chat service dependency.
        user: Authenticated user dependency.

    Returns:
        Response with the created chat ID.

    Raises:
        HTTPException: If file upload or processing fails.
    """
    try:
        validate_file(file)
        meta = FileMeta.from_upload(file=file)
        original_doc = save_upload_to_minio(file=file)
        if not original_doc:
            logger.error("Failed to upload the file missing file path", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload to file",
            )

        chat_id = chat_services.create_chat(
            user_id=user.user_id, title=meta.filename, original_doc=original_doc
        )

        return {
            "message": "Successfully saved the docs",
            "status": Status.success,
            "data": chat_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to file",
        )
