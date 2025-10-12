from utils.celery import celery


@celery.task
async def extract_text_from_yt_link(file_path: str, link: str) -> str:
    return "Extracted text from YouTube link"
