from input_api.src.lib.celery import celery


@celery.task
async def extract_text_from_images(file_path: str, file_type: str) -> str:
    return "Extracted text from images"
