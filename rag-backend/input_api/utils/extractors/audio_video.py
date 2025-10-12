from utils.celery import celery


@celery.task
async def extract_text_audio_video(file_path: str, file_type: str) -> str:
    return "Extracted text from audio or video"
