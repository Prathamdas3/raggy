from uuid import uuid4
from app.core import get_logger, boto_client, ContentType, BucketName


logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ContentType.PDF,
    "audio/mpeg": ContentType.MP3,
    "audio/wav": ContentType.WAV,
}


async def save_upload_to_minio(filename:str,content_type:str,file_bytes:bytes) -> str:
    """
    Read uploaded file bytes and save directly to MinIO.
    Returns storage_key → store this in DB to retrieve later.
    e.g. "documents/uuid4.pdf"
    """
    if not filename or not filename.strip():
        raise ValueError("No file name provided.")

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported file type: {content_type}.")

    try:
        object_name = f"{uuid4()}{_get_extension(content_type)}"

        storage_key =await  boto_client.save_file(
            bucket_name=BucketName.DOCUMENTS,
            object_name=object_name,
            data=file_bytes,
            content_type=ALLOWED_CONTENT_TYPES[content_type],
            metadata={"original_filename": filename},
        )
        return storage_key

    except ValueError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to save upload to MinIO: {e}",
        )
        raise RuntimeError(f"Failed to save file: {e}") from e


def _get_extension(content_type: str) -> str:
    return {
        "application/pdf": ".pdf",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
    }.get(content_type, "")
