"""Application configuration.

Loads and validates settings from environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from functools import lru_cache
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parents[1]
TEMP_DIR = BASE_DIR / "temp"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        temp_dir: Directory for temporary files.
        env: Application environment (development, production).
        debug: Enable debug mode.
        model_id: ML model identifier.
        huggingface_api_token: HuggingFace API token.
        huggingface_model: HuggingFace model name.
        huggingface_device: Device for inference (cpu/cuda).
        database_url: PostgreSQL database URL.
        access_token_expire_minutes: Access token expiration time.
        refresh_token_expire_days: Refresh token expiration time.
        secret_key: JWT secret key.
        algorithm: JWT algorithm (default HS256).
        frontend_url: Frontend application URL.
        backend_url: Backend application URL.
        redis_host: Redis host.
        redis_port: Redis port.
        qdrant_url: Qdrant server URL.
        qdrant_collection_name: Qdrant collection name.
        qdrant_vector_size: Embedding vector size.
        qdrant_use_https: Use HTTPS for Qdrant.
    """

    temp_dir: Path = TEMP_DIR
    env: str = Field(validation_alias="ENV", default="development")
    debug: bool = Field(validation_alias="DEBUG", default=False)
    model_id: str = Field(validation_alias="MODEL_ID", default="")
    huggingface_api_token: str = Field(
        validation_alias="HUGGINGFACE_API_TOKEN", default=""
    )
    huggingface_model: str = Field(validation_alias="HUGGINGFACE_MODEL", default="")
    huggingface_device: str = Field(
        validation_alias="HUGGINGFACE_DEVICE", default="cpu"
    )
    database_url: str = Field(validation_alias="DATABASE_URL", default="")
    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )
    refresh_token_expire_days: int = Field(
        validation_alias="REFRESH_TOKEN_EXPIRE_DAYS", default=7
    )
    secret_key: str = Field(validation_alias="SECRET_KEY", default="")
    algorithm: str = Field(validation_alias="ALGORITHM", default="HS256")
    frontend_url: str = Field(
        validation_alias="FRONTEND_URL", default="http://localhost:3000"
    )
    backend_url: str = Field(
        validation_alias="BACKEND_URL", default="http://localhost:9000"
    )

    redis_host: str = Field(validation_alias="REDIS_HOST", default="redis")
    redis_port: int = Field(validation_alias="REDIS_PORT", default=6379)

    qdrant_url: str = Field(
        validation_alias="QDRANT_URL", default="http://localhost:6333"
    )
    qdrant_collection_name: str = Field(
        validation_alias="QDRANT_COLLECTION_NAME", default="documents"
    )
    qdrant_vector_size: int = Field(validation_alias="QDRANT_VECTOR_SIZE", default=384)
    qdrant_use_https: bool = Field(validation_alias="QDRANT_USE_HTTPS", default=False)

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_config() -> Settings:
    """Get cached application settings instance.

    Returns:
        Cached Settings instance.
    """
    return Settings()


config = get_config()
