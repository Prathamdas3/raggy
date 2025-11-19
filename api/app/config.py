import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_DIR = BASE_DIR / "temp"


@dataclass
class Configs:
    TEMP_DIR: Path = TEMP_DIR
    MODEL_ID: str = os.getenv("MODEL_ID", "")
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    DATABASE_URI: str = os.getenv("DATABASE_URI", "")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "")
    HUGGINGFACE_DEVICE: str = os.getenv("HUGGINGFACE_DEVICE", "cpu")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "")
    HUGGINGFACE_DEVICE: str = os.getenv("HUGGINGFACE_DEVICE", "cpu")

    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    QDRANT_VECTOR_SIZE: int = int(os.getenv("QDRANT_VECTOR_SIZE", "384"))
    QDRANT_USE_HTTPS: bool = bool(os.getenv("QDRANT_USE_HTTPS", "false"))

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "audio-files")
    MINIO_SECURE: str = os.getenv("MINIO_SECURE", "false")

    REDIS_HOST: str = str(os.getenv("REDIS_HOST", "localhost"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    RATE_LIMIT_ENABLED: bool = bool(os.getenv("RATE_LIMIT_ENABLED", "true"))
    RATE_LIMIT_TIMES: int = int(os.getenv("RATE_LIMIT_TIMES", "100"))
    RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

    class Config:
        env_file = ".env"


config = Configs()
