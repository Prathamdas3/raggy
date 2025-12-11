from minio import Minio
from minio.error import S3Error
from app.utils.logger import get_logger
from typing import Optional, TypeVar
from app.config import config
import threading

T = TypeVar("T")
logger = get_logger(__name__)


class MinIOClientSingleton:
    """
    Singleton class for MinIO client to ensure only one instance is created
    and reused across all workers and requests.
    """

    _instance: Optional[type[T]] = None
    _lock = threading.Lock()
    _initialized = False

    @classmethod
    def get_client(cls) -> Minio:
        """
        Get or create the MinIO client instance.
        Thread-safe singleton implementation.

        Returns:
            Minio: The MinIO client instance

        Raises:
            RuntimeError: If client initialization fails
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    try:
                        logger.debug("Initializing MinIO client singleton...")
                        logger.debug(f"MinIO Endpoint: {config.MINIO_ENDPOINT}")
                        logger.debug(f"MinIO Bucket: {config.MINIO_BUCKET_NAME}")
                        logger.debug(f"MinIO Secure: {config.MINIO_SECURE}")

                        cls._instance = Minio(
                            endpoint=config.MINIO_ENDPOINT,
                            access_key=config.MINIO_ACCESS_KEY,
                            secret_key=config.MINIO_SECRET_KEY,
                            secure=config.MINIO_SECURE,
                        )

                        cls._initialized = True
                        logger.info("✓ MinIO client singleton initialized successfully")

                    except Exception as e:
                        logger.error(f"✗ Failed to initialize MinIO client: {str(e)}")
                        logger.error("Check your MinIO configuration")
                        logger.error(f"MINIO_ENDPOINT={config.MINIO_ENDPOINT}")
                        logger.error(f"MINIO_BUCKET_NAME={config.MINIO_BUCKET_NAME}")
                        cls._instance = None
                        raise RuntimeError(
                            f"Failed to initialize MinIO client: {str(e)}. "
                            f"Please check your MinIO configuration and ensure the service is running."
                        )

        return cls._instance

    @classmethod
    def initialize_bucket(cls) -> None:
        """
        Ensure the bucket exists, create it if it doesn't.
        Should be called during application startup.

        Raises:
            S3Error: If bucket operations fail
        """
        try:
            client = cls.get_client()

            if not client.bucket_exists(config.MINIO_BUCKET_NAME):
                logger.info(
                    f"Bucket '{config.MINIO_BUCKET_NAME}' does not exist. Creating..."
                )
                client.make_bucket(config.MINIO_BUCKET_NAME)
                logger.info(
                    f"✓ Bucket '{config.MINIO_BUCKET_NAME}' created successfully"
                )
            else:
                logger.info(f"✓ Bucket '{config.MINIO_BUCKET_NAME}' already exists")

        except S3Error as e:
            logger.error(f"✗ Error with bucket operations: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error during bucket initialization: {str(e)}")
            raise

    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if the MinIO client has been initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        return cls._initialized

    @classmethod
    def health_check(cls) -> dict:
        """
        Perform a health check on the MinIO connection.

        Returns:
            dict: Health check status
        """
        try:
            client = cls.get_client()
            bucket_exists = client.bucket_exists(config.MINIO_BUCKET_NAME)

            return {
                "healthy": True,
                "client_initialized": cls._initialized,
                "bucket_exists": bucket_exists,
                "bucket_name": config.MINIO_BUCKET_NAME,
                "endpoint": config.MINIO_ENDPOINT,
            }
        except Exception as e:
            logger.error(f"MinIO health check failed: {str(e)}")
            return {
                "healthy": False,
                "client_initialized": cls._initialized,
                "error": str(e),
                "endpoint": config.MINIO_ENDPOINT,
            }

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance. Useful for testing or reconnection scenarios.
        """
        with cls._lock:
            logger.warning("Resetting MinIO client singleton")
            cls._instance = None
            cls._initialized = False


# Convenience functions
def get_minio_client() -> Minio:
    """
    Get the MinIO client singleton instance.

    Returns:
        Minio: The MinIO client instance
    """
    return MinIOClientSingleton.get_client()


def get_bucket_name() -> str:
    """
    Get the configured MinIO bucket name.

    Returns:
        str: The bucket name
    """
    return config.MINIO_BUCKET_NAME


def initialize_minio() -> None:
    """
    Initialize MinIO client and ensure bucket exists.
    Call this during application startup.
    """
    MinIOClientSingleton.initialize_bucket()


def minio_health_check() -> dict:
    """
    Perform MinIO health check.

    Returns:
        dict: Health check results
    """
    return MinIOClientSingleton.health_check()
