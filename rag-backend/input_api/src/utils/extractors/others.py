from utils.celery import celery
from pydentic_models import SuccessResponse, ErrorResponse
from utils.logger import get_logger
import fitz  # pymupdf
import os

logger = get_logger("utils/extractors/others")


@celery.task(bind=True)
def extract_text_from_othertypes(file_path: str, file_type: str):
    """
    Extract text from supported file types (PDF for now).
    Returns a standardized response with extracted text.
    """
    logger.info(f"Starting text extraction: {file_path} of type {file_type}")

    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return ErrorResponse(status="error", message="File not found", code=404)

    text = ""

    try:
        if file_type == "application/pdf":
            logger.info(f"Extracting text from PDF file: {file_path}")
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            logger.info(f"Text extraction completed: {file_path}")
            print(text)
            return SuccessResponse(
                data={"text": text}, message="Text extracted successfully"
            )
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return ErrorResponse(
                status="error", message=f"Unsupported file type: {file_type}", code=400
            )

    except Exception as e:
        logger.exception(f"Error extracting text from file: {file_path}")
        return ErrorResponse(status="error", message=str(e), code=500)
