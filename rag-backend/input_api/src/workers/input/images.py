from lib.celery import celery
from utils.converters.png_to_text import extract_text_from_image
from lib.logger import get_logger
from utils.response import APIError

logger = get_logger("workers/images")


@celery.task(bind=True)
def extract_text_from_image_task(
    self, image_file_path: str, file_type: str, user_id: str = None, chat_id: str = None
) -> dict:
    """
    Celery task to extract text from image using OCR and queue for splitting.

    Process:
    1. Convert image to PNG
    2. Extract text from PNG using OCR
    3. Delete PNG file
    4. Queue extracted text for splitting into chunks
    5. Return extracted text and split task ID

    Args:
        image_file_path: Path to the image file
        file_type: MIME type of the image
        user_id: Optional user ID for tracking
        chat_id: Optional chat ID for tracking

    Returns:
        dict: {
            "status": "success"/"error"/"partial_success",
            "data": {...},
            "message": "...",
            "code": 200/400/500/206
        }
    """
    logger.info(f"Celery task started: extract_text_from_image_task")
    logger.info(
        f"Image: {image_file_path}, Type: {file_type}, User: {user_id}, Chat: {chat_id}"
    )

    # Set defaults for user_id and chat_id if not provided
    user_id = user_id or "unknown"
    chat_id = chat_id or "unknown"

    import asyncio

    try:
        # ===== Input Validation =====
        if not image_file_path:
            logger.error("Empty image file path provided")
            return {
                "status": "error",
                "message": "Image file path cannot be empty",
                "code": 400,
                "data": None,
            }

        if not file_type:
            logger.error("File type not provided")
            return {
                "status": "error",
                "message": "File type must be specified",
                "code": 400,
                "data": None,
            }

        # ===== Extract Text from Image =====
        logger.info("Step 1: Extracting text from image using OCR")

        try:
            extracted_text = asyncio.run(
                extract_text_from_image(image_file_path, file_type)
            )
            logger.info(
                f"Text extraction successful. Text length: {len(extracted_text)} characters"
            )

        except APIError as ae:
            logger.error(f"Text extraction failed: {ae.message}")
            return {
                "status": "error",
                "message": ae.message,
                "code": ae.status_code,
                "data": None,
            }

        except Exception as e:
            logger.error(f"Unexpected error during text extraction: {str(e)}")
            logger.exception(f"Error details: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during text extraction",
                "code": 500,
                "data": None,
            }

        # Validate extracted text
        if not extracted_text or not extracted_text.strip():
            logger.warning(f"No text extracted from image: {image_file_path}")
            return {
                "status": "error",
                "message": "No text found in image",
                "code": 400,
                "data": None,
            }

        # ===== Queue Text for Splitting =====
        logger.info("Step 2: Queueing text for splitting")

        split_task_id = None
        split_error = None

        try:
            from workers.input.text_splitter import split_text_task

            split_task = split_text_task.delay(extracted_text, user_id, chat_id)
            split_task_id = split_task.id
            logger.info(f"Queued split_text_task {split_task_id} for extracted text")

        except Exception as se:
            logger.error(f"Failed to queue split_text_task: {str(se)}")
            split_error = str(se)

        # ===== Return Response =====
        logger.info("Text extraction task completed")

        if split_task_id:
            logger.info(
                f"Extraction and splitting successful. Split task ID: {split_task_id}"
            )
            return {
                "status": "success",
                "message": "Text extracted from image and queued for splitting successfully",
                "code": 200,
                "data": {
                    "extracted_text": extracted_text,
                    "text_length": len(extracted_text),
                    "file_type": file_type,
                    "split_task_id": split_task_id,
                },
            }
        else:
            # Extraction succeeded but splitting failed
            logger.warning(f"Extraction succeeded but splitting failed: {split_error}")
            return {
                "status": "partial_success",
                "message": "Text extracted from image but failed to queue for splitting",
                "code": 206,  # 206 Partial Content
                "data": {
                    "extracted_text": extracted_text,
                    "text_length": len(extracted_text),
                    "file_type": file_type,
                    "split_error": split_error,
                },
            }

    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_image_task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during image processing",
            "code": 500,
            "data": None,
        }
