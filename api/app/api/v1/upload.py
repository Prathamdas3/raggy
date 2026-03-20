"""File upload API endpoints.

Provides endpoints for uploading and processing files including PDFs.
"""

from fastapi import APIRouter, status, UploadFile, File, HTTPException, Depends
from app.core import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models import Response, FileMeta, Status
from app.utils import save_file, extract_pdf_content_from_path
from app.services import get_chat_service, ChatService
from app.api.v1.auth import get_user_id, RefreshTokenUserId


file_router = APIRouter(prefix="/upload")
logger = get_logger()

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)


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
        meta = FileMeta.from_upload(file=file)
        file_path = save_file(file=file, file_type=meta.category)
        if not file_path:
            logger.error("Failed to upload the file missing file path", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload to file",
            )

        doc_id = chat_services.create_chat(user_id=user.user_id)
        extract_pdf_content_from_path(path=file_path)
        return {
            "message": "Successfully saved the docs",
            "status": Status.success,
            "data": doc_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to file",
        )
