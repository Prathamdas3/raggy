from utils.response import APIError
from lib.celery import celery
from lib.logger import get_logger
from utils.converters.audio_video_to_wav import convert_audio_video_to_wav
from utils.converters.wav_to_text import transcribe_audio

logger = get_logger("utils/extractors/audio_video")


@celery.task(bind=True)
def extract_text_from_wav(self, file_path: str, file_type: str) -> dict:
    """
    Celery task to convert audio/video to WAV and transcribe to text.

    Process:
    1. Convert audio/video file to WAV format
    2. Transcribe WAV audio to text using Whisper
    3. Delete intermediate files
    4. Return transcribed text

    Args:
        file_path: Path to the audio or video file
        file_type: MIME type of the file

    Returns:
        dict: {
            "status": "success"/"error",
            "data": {"transcribed_text": "...", "wav_path": "..."},
            "message": "...",
            "code": 200/400/500
        }
    """
    logger.info(f"Celery task started: extract_text_from_wav")
    logger.info(f"File: {file_path}, Type: {file_type}")

    wav_file_path = None
    import asyncio

    try:
        # ===== Step 1: Convert to WAV =====
        logger.info("Step 1: Converting audio/video to WAV format")
        try:
            wav_file_path = asyncio.run(
                convert_audio_video_to_wav(file_path, file_type)
            )
            logger.info(f"Conversion successful. WAV path: {wav_file_path}")
        except APIError as ae:
            logger.error(f"WAV conversion failed: {ae.message}")
            return {
                "status": "error",
                "message": f"WAV conversion failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }
        except Exception as e:
            logger.error(f"Unexpected error during WAV conversion: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during WAV conversion",
                "code": 500,
                "data": None,
            }

        # ===== Step 2: Transcribe WAV to Text =====
        logger.info("Step 2: Transcribing WAV audio to text")
        try:
            # Run async transcription in sync context
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

        # ===== Step 3: Return Success =====
        logger.info("extract_text_from_wav task completed successfully")
        return {
            "status": "success",
            "message": "Audio extracted and transcribed successfully",
            "code": 200,
            "data": {
                "transcribed_text": transcribed_text,
                "wav_path": wav_file_path,
                "file_type": "audio/wav",
            },
        }

    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_wav task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during task execution",
            "code": 500,
            "data": None,
        }
