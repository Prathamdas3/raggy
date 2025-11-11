from app.utils.logger import get_logger
from pathlib import Path
from uuid import UUID
from app.configs.minio import get_minio_client, get_bucket_name
from minio import S3Error
from fastapi import HTTPException, status
from datetime import timedelta
from app.utils.file import remove_file

logger = get_logger(__name__)


def save_audio_minio(path: Path, chat_id: UUID) -> str:
    if not path or not isinstance(path, Path):
        raise TypeError("Not a valid path provided")

    if not chat_id or not isinstance(chat_id, UUID):
        raise TypeError("Chat id is should be a valid UUID")

    try:
        logger.debug(f"Starting Minio upload for chat_id: {chat_id}, file path: {path}")
        minio_client = get_minio_client()
        bucket_name = get_bucket_name()
    except Exception as e:
        logger.error(f"Failed to get the minio client and bucket: {str(e)}")
        raise ValueError("Failed to get the minio client")

    if not path.exists():
        logger.error(f"Temp file does not exist: {path}", exc_info=True)
        raise FileNotFoundError("File not found for the given path")

    if not path.is_file():
        logger.error(f"Path is not a file: {path}", exc_info=True)
        raise IsADirectoryError("given path is a folder not a file")

    file_size = path.stat().st_size()
    if file_size == 0:
        logger.error(f"Given file path content is empty: {path}")

    file_name = path.name
    minio_object_name = f"audio/{chat_id}/{file_name}"

    logger.debug(f"Uploading file to minio: {minio_object_name}")

    try:
        result = minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=minio_object_name,
            file_path=str(path),
            content_type="audio/mpeg",
        )
        logger.debug(
            f"Upload result - ETag: {result.etag}, Version: {result.version_id}"
        )

    except S3Error as se:
        logger.error(f"S3Error during upload: {str(se)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload the audio to minio",
        )

    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload teh audio",
        )

    try:
        stat = minio_client.stat_object(
            bucket_name=bucket_name, minio_object_name=minio_object_name
        )
        logger.debug(f"Upload verified, object size: {stat.size}", exc_info=True)

        if stat.size != file_size:
            logger.warnning(
                f"File size mismatch, Original: {file_size}, Uploaded: {stat.size}"
            )
    except S3Error as se:
        logger.error(f"Failed to verify uploaded object: {str(se)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify the uploaded the audio to minio",
        )

    try:
        minio_url = minio_client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=minio_object_name,
            expires=timedelta(days=7),
        )

        logger.debug(f"Generated presigned URL(truncated): {minio_url[:100]}....")

    except Exception as e:
        logger.warning(f"Faield to generate presigned URL: {str(e)}")
        from app.configs.minio import MINIO_ENDPOINT, MINIO_SECURE

        protocol = "https" if MINIO_SECURE else "http"
        minio_url = f"{protocol}://{MINIO_ENDPOINT}/{bucket_name}/{minio_object_name}"

    try:
        remove_file(file_path=path)
    except Exception:
        raise

    return minio_url
