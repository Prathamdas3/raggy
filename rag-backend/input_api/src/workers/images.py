from lib.celery import celery
from utils.converters.png_to_text import extract_text_from_image
from lib.logger import get_logger
from utils.response import APIError
logger = get_logger("workers/images")

@celery.task(bind=True)
def extract_text_from_image_task(self, image_file_path: str, file_type: str) -> dict:
    """
    Celery task to extract text from image using OCR.
    
    Process:
    1. Convert image to PNG
    2. Extract text from PNG using OCR
    3. Delete PNG file
    4. Return extracted text
    
    Args:
        image_file_path: Path to the image file
        file_type: MIME type of the image
        
    Returns:
        dict: {"status": "success"/"error", "data": {...}, "message": "...", "code": 200/400/500}
    """

    
    logger.info(f"Celery task started: extract_text_from_image_task")
    import asyncio
    try:
        # Run async function
        extracted_text = asyncio.run(extract_text_from_image(image_file_path, file_type))
        
        logger.info("Text extraction task completed successfully")
        return {
            "status": "success",
            "message": "Text extracted from image successfully",
            "code": 200,
            "data": {
                "extracted_text": extracted_text
            }
        }
    
    except APIError as ae:
        logger.error(f"Text extraction task failed: {ae.message}")
        return {
            "status": "error",
            "message": ae.message,
            "code": ae.status_code,
            "data": None
        }
    
    except Exception as e:
        logger.exception(f"Unexpected error in text extraction task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during text extraction",
            "code": 500,
            "data": None
        }