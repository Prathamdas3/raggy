from fastapi import UploadFile, status
from uuid import uuid4
from app.core import AppException
from app.core import get_logger, minio_client, ContentType, BucketName


logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ContentType.PDF,
    "audio/mpeg": ContentType.MP3,
    "audio/wav": ContentType.WAV,
}


# ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_and_read(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise AppException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            message=f"Only PDF files are allowed. Got: {file.content_type}",
        )
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise AppException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            message="File size exceeds the 10MB limit.",
        )
    return contents  # caller owns the bytes, no seek needed


def save_bytes_to_minio(file: UploadFile, contents: bytes,filename:str,content_type:str) -> str:


    object_name = f"{uuid4()}{_get_extension(content_type)}"
    storage_key = minio_client.save_file(
        bucket_name=BucketName.DOCUMENTS,
        object_name=object_name,
        data=contents,
        content_type=ALLOWED_CONTENT_TYPES[content_type],
        metadata={"original_filename": file.filename},
    )
    return storage_key


def _get_extension(content_type: str) -> str:
    return {
        "application/pdf": ".pdf",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
    }.get(content_type, "")
