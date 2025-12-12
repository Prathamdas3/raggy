from app.utils.logger import get_logger
from pathlib import Path
from uuid import UUID
from app.configs.minio import get_minio_client, get_bucket_name
from minio import S3Error
from fastapi import HTTPException
# from datetime import timedelta
from app.config import config
from app.utils.remove_file import remove_file

logger = get_logger(__name__)


def upload_to_minio(
    file_path: Path,
    chat_id: UUID,
    folder: str,
    content_type: str,
    expires_days: int = 7,
) -> str:
    if not file_path or not isinstance(file_path, Path):
        raise TypeError("Invalid file path")

    if not chat_id or not isinstance(chat_id, UUID):
        raise TypeError("Invalid chat ID")

    minio = get_minio_client()
    bucket = get_bucket_name()

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")

    file_name = file_path.name
    object_name = f"{folder}/{chat_id}/{file_name}"

    try:
        minio.fput_object(
            bucket,
            object_name,
            str(file_path),
            content_type=content_type,
        )
    except S3Error as e:
        raise HTTPException(500, f"Failed to upload file: {e}")

    # Verify
    stat = minio.stat_object(bucket, object_name)
    if stat.size != file_path.stat().st_size:
        logger.warning("File size mismatch after upload!")

    # Presigned URL
    # try:
    #     url = minio.presigned_get_object(
    #         bucket_name=bucket,
    #         object_name=object_name,
    #         expires=timedelta(days=expires_days),
    #     )
    # except Exception:
    #     raise

        # from app.configs.minio import MINIO_ENDPOINT, MINIO_SECURE

        # protocol = "https" if MINIO_SECURE else "http"
        # url = f"{protocol}://{MINIO_ENDPOINT}/{bucket}/{object_name}"

    # Optionally delete local file
    try:
        remove_file(file_path)
    except Exception:
        pass

    backend_url = config.BACKEND_URL or "http://localhost:8000"
    proxy_url = f"{backend_url}/api/v1/files/{bucket}/{object_name}"

    logger.debug(f"Generated proxy URL: {proxy_url}")

    return proxy_url
