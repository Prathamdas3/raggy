import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# This loads local .env during development only (NOT used in Docker)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_DIR = BASE_DIR / "temp"


def to_bool(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "on")


@dataclass
class Configs:
    TEMP_DIR: Path = TEMP_DIR

    # General
    ENV: str = os.getenv("ENV", "")
    MODEL_ID: str = os.getenv("MODEL_ID", "")
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    DATABASE_URI: str = os.getenv("DATABASE_URI", "")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "")
    HUGGINGFACE_DEVICE: str = os.getenv("HUGGINGFACE_DEVICE", "cpu")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Redis (IMPORTANT)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # Qdrant
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    QDRANT_VECTOR_SIZE: int = int(os.getenv("QDRANT_VECTOR_SIZE", 384))
    QDRANT_USE_HTTPS: bool = to_bool(os.getenv("QDRANT_USE_HTTPS", "false"))

    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "audio-files")
    MINIO_SECURE: bool = to_bool(os.getenv("MINIO_SECURE", "false"))

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = to_bool(os.getenv("RATE_LIMIT_ENABLED", "true"))
    RATE_LIMIT_TIMES: int = int(os.getenv("RATE_LIMIT_TIMES", 10))
    RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", 60))


config = Configs()
