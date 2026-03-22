from io import BytesIO
from gtts import gTTS
from app.core import get_logger, minio_client, BucketName, ContentType
from uuid import uuid4

logger = get_logger(__name__)


def text_to_audio(text: str, chat_id) -> str:
    """
    Convert text to audio and save directly to MinIO.
    Returns storage_key → store this in DB.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string.")
    try:
        buffer = BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buffer)
        buffer.seek(0)

        storage_key = minio_client.save_file(
            bucket_name=BucketName.AUDIO,
            object_name=f"{chat_id}_{uuid4()}.mp3",
            data=buffer.read(),
            content_type=ContentType.MP3,
            metadata={"chat_id": chat_id},
        )
        return storage_key
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to convert text to audio: {e}")
        raise RuntimeError(f"Failed to convert text to audio: {e}") from e
