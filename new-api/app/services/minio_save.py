from app.utils.logger import get_logger
from pathlib import Path
from uuid import UUID
from app.configs.minio import get_minio_client, get_bucket_name

logger = get_logger(__name__)


def save_audio_minio(path: Path, chat_id: UUID):
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
        logger.error(f"Path is not a file: {path}",exc_info=True)
        raise IsADirectoryError("given path is a folder not a file")
    
    file_size=path.stat().st_size()
    
