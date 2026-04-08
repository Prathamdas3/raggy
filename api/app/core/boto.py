# app/core/minio.py
from io import BytesIO
from datetime import timedelta
import asyncio
import aioboto3
from botocore.exceptions import ClientError
from app.core import get_logger, config

logger = get_logger(__name__)


class ContentType:
    PDF = "application/pdf"
    MP3 = "audio/mpeg"
    WAV = "audio/wav"


class BucketName:
    DOCUMENTS = "documents"
    AUDIO = "audio"
    EXPORTS = "exports"


class BotoClient:
    _lock = asyncio.Lock()
    _session: aioboto3.Session | None = None

    @classmethod
    def _get_session(cls) -> aioboto3.Session:
        """Session is cheap to create and thread-safe — just lazily init once."""
        if cls._session is None:
            cls._session = aioboto3.Session()
        return cls._session

    @classmethod
    def _client(cls):
        """Returns async context manager for S3 client."""
        return cls._get_session().client(
            "s3",
            endpoint_url=f"{'https' if config.minio_secure else 'http'}://{config.minio_endpoint}",
            aws_access_key_id=config.minio_access_key,
            aws_secret_access_key=config.minio_secret_key,
            region_name="us-east-1",  # required by boto3, ignored by MinIO
        )

    @classmethod
    async def _ensure_bucket(cls, s3, bucket_name: str) -> None:
        """Takes an already-open client to avoid nested context managers."""
        try:
            await s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                await s3.create_bucket(Bucket=bucket_name)
                logger.info(f"Bucket '{bucket_name}' created.")
            else:
                logger.error(f"Failed to ensure bucket '{bucket_name}': {e}")
                raise

    @classmethod
    async def save_file(
        cls,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        try:
            async with cls._client() as s3:
                await cls._ensure_bucket(s3, bucket_name)
                await s3.put_object(
                    Bucket=bucket_name,
                    Key=object_name,
                    Body=BytesIO(data),
                    ContentType=content_type,
                    Metadata=metadata or {},
                )
            storage_key = f"{bucket_name}/{object_name}"
            logger.info(f"Saved '{storage_key}'.")
            return storage_key
        except ClientError as e:
            logger.error(f"Failed to save '{object_name}': {e}")
            raise

    @classmethod
    async def get_file(cls, bucket_name: str, object_name: str) -> bytes:
        try:
            async with cls._client() as s3:
                response = await s3.get_object(Bucket=bucket_name, Key=object_name)
                return await response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to get file '{object_name}': {e}")
            raise

    @classmethod
    async def get_url(
        cls,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        try:
            async with cls._client() as s3:
                return await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=int(expires.total_seconds()),
                )
        except ClientError as e:
            logger.error(f"Failed to get URL for '{object_name}': {e}")
            raise

    @classmethod
    async def get_metadata(cls, bucket_name: str, object_name: str) -> dict:
        try:
            async with cls._client() as s3:
                stat = await s3.head_object(Bucket=bucket_name, Key=object_name)
            return {
                "object_name": object_name,
                "size": stat["ContentLength"],
                "content_type": stat["ContentType"],
                "last_modified": stat["LastModified"],
                "metadata": stat.get("Metadata", {}),
            }
        except ClientError as e:
            logger.error(f"Failed to get metadata for '{object_name}': {e}")
            raise

    @classmethod
    async def delete_file(cls, bucket_name: str, object_name: str) -> None:
        try:
            async with cls._client() as s3:
                await s3.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info(f"Deleted '{object_name}' from '{bucket_name}'.")
        except ClientError as e:
            logger.error(f"Failed to delete '{object_name}': {e}")
            raise

    @classmethod
    async def initialize(cls) -> None:
        """Call at startup — ensures session and all buckets are ready."""
        async with cls._client() as s3:
            for bucket in [BucketName.DOCUMENTS, BucketName.AUDIO, BucketName.EXPORTS]:
                await cls._ensure_bucket(s3, bucket)
        logger.info("MinIO client initialized.")

    @classmethod
    def reset(cls) -> None:
        cls._session = None
        logger.warning("MinIO client reset.")


boto_client = BotoClient()