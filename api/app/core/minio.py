from io import BytesIO
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from app.core import get_logger, config
import threading

logger = get_logger(__name__)


class ContentType:
    PDF = "application/pdf"
    MP3 = "audio/mpeg"
    WAV = "audio/wav"


class BucketName:
    DOCUMENTS = "documents"  # user uploaded files
    AUDIO = "audio"  # tts generated audio
    EXPORTS = "exports"  # generated pdfs shared with user


class MinIOClient:
    _lock = threading.RLock()
    _client: Minio | None = None

    @classmethod
    def _get_client(cls) -> Minio:
        if cls._client is None:
            with cls._lock:
                if cls._client is None:
                    try:
                        cls._client = Minio(
                            endpoint=config.minio_endpoint,
                            access_key=config.minio_access_key,
                            secret_key=config.minio_secret_key,
                            secure=config.minio_secure,
                        )
                        logger.info("MinIO client initialized.")
                    except Exception as e:
                        cls._client = None
                        logger.error(f"Failed to initialize MinIO client: {e}")
                        raise RuntimeError(
                            f"Failed to initialize MinIO client: {e}"
                        ) from e
        if cls._client is None:
            raise RuntimeError("MinIO client could not be initialized.")
        return cls._client

    @classmethod
    def _ensure_bucket(cls, bucket_name: str) -> None:
        try:
            client = cls._get_client()
            if not client.bucket_exists(bucket_name=bucket_name):
                client.make_bucket(bucket_name=bucket_name)
                logger.info(f"Bucket '{bucket_name}' created.")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket '{bucket_name}': {e}")
            raise

    @classmethod
    def save_file(
        cls,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """
        Save bytes to MinIO.
        Returns full storage key → store this in DB to retrieve later.
        e.g. "documents/doc_123.pdf"
        """
        try:
            cls._ensure_bucket(bucket_name)
            cls._get_client().put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type,
                metadata=metadata,
            )
            storage_key = f"{bucket_name}/{object_name}"
            logger.info(f"Saved '{storage_key}'.")
            return storage_key  # ← store this in DB
        except S3Error as e:
            logger.error(f"Failed to save '{object_name}': {e}")
            raise

    @classmethod
    def get_file(cls, bucket_name: str, object_name: str) -> bytes:
        """
        Download file as bytes.
        Use for: extracting content from uploaded PDFs,
                 reading audio for processing.
        """
        response = None
        try:
            response = cls._get_client().get_object(
                bucket_name=bucket_name,
                object_name=object_name,
            )
            return response.read()
        except S3Error as e:
            logger.error(f"Failed to get file '{object_name}': {e}")
            raise
        finally:
            if response:
                response.close()
                response.release_conn()

    @classmethod
    def get_url(
        cls,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        Returns a presigned URL.
        Use for: sharing generated PDFs with users,
                 serving audio to frontend.
        Adjust expires per usecase:
            - internal processing → timedelta(minutes=15)
            - user facing audio   → timedelta(hours=1)
            - shared pdf export   → timedelta(days=7)
        """
        try:
            return cls._get_client().presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires,
            )
        except S3Error as e:
            logger.error(f"Failed to get URL for '{object_name}': {e}")
            raise

    @classmethod
    def get_metadata(cls, bucket_name: str, object_name: str) -> dict:
        """
        Returns file metadata without downloading the file.
        Use for: checking file size, type, upload time before processing.
        """
        try:
            stat = cls._get_client().stat_object(
                bucket_name=bucket_name,
                object_name=object_name,
            )
            return {
                "object_name": stat.object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata,
            }
        except S3Error as e:
            logger.error(f"Failed to get metadata for '{object_name}': {e}")
            raise

    @classmethod
    def delete_file(cls, bucket_name: str, object_name: str) -> None:
        try:
            cls._get_client().remove_object(
                bucket_name=bucket_name,
                object_name=object_name,
            )
            logger.info(f"Deleted '{object_name}' from '{bucket_name}'.")
        except S3Error as e:
            logger.error(f"Failed to delete '{object_name}': {e}")
            raise

    @classmethod
    def initialize(cls) -> None:
        """Call at startup — ensures client and all buckets are ready."""
        cls._get_client()
        for bucket in [BucketName.DOCUMENTS, BucketName.AUDIO, BucketName.EXPORTS]:
            cls._ensure_bucket(bucket)

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._client = None
            logger.warning("MinIO client reset.")


minio_client = MinIOClient()
