from lib.celery import celery
from utils.response import APIError
from lib.logger import get_logger
from utils.converters.yt_link_to_wav import save_youtube_audio_as_wav
from utils.converters.wav_to_text import transcribe_audio

logger = get_logger("utils/extractors/yt_link")


@celery.task(bind=True)
def extract_text_from_yt_link(self, link: str) -> dict:
    """
    Celery task to process a YouTube link and extract text.
    Args:
        link: YouTube video URL

    Returns:
        dict: {
            "status": "success"/"error",
            "data": {"extracted_text": "..."},
            "message": "...",
            "code": 200/400/500
        }
    """
    logger.info(f"Celery task started: extract_text_from_yt_link")
    logger.info(f"Link: {link} ")

    wav_file_path = None

    try:
        logger.info("Step 1: Saving YouTube audio as WAV")
        import asyncio

        try:
            wav_file_path = asyncio.run(save_youtube_audio_as_wav(link))
            logger.info(f"WAV file saved successfully at: {wav_file_path}")
        except APIError as ae:
            logger.error(f"WAV saving failed: {ae.message}")
            return {
                "status": "error",
                "message": f"WAV saving failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }
        except Exception as ve:
            logger.error(f"Invalid YouTube link: {ve}")
            return {
                "status": "error",
                "message": f"Invalid YouTube link: {ve}",
                "code": 400,
                "data": None,
            }

        logger.info("Step 2: Transcribing WAV audio to text")
        try:
            transcribed_text = asyncio.run(transcribe_audio(wav_file_path))
            logger.info(
                f"Transcription successful. Text length: {len(transcribed_text)} characters"
            )
        except APIError as ae:
            logger.error(f"Transcription failed: {ae.message}")
            return {
                "status": "error",
                "message": f"Transcription failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during transcription",
                "code": 500,
                "data": None,
            }

        logger.info("extract_text_from_yt_link completed successfully")
        return {
            "status": "success",
            "message": "Text extracted successfully from YouTube link",
            "code": 200,
            "data": {
                "extracted_text": transcribed_text,
                "wav_file_path": str(wav_file_path),
                "file_type": "yt_link, audio/wav",
            },
        }

    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_yt_link: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected server error",
            "code": 500,
            "data": None,
        }
