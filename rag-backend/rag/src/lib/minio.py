from minio import Minio
from minio.error import S3Error
import logging

logger = logging.getLogger("lib/minio")

# MinIO Configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
BUCKET_NAME = "audio-files"

# Create MinIO client
client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def initialize_minio():
    """Create bucket if it doesn't exist"""
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            logger.info(f"✓ Bucket '{BUCKET_NAME}' created successfully")
        else:
            logger.info(f"✓ Bucket '{BUCKET_NAME}' already exists")
    except S3Error as e:
        logger.error(f"✗ Error creating bucket: {e}")
        raise