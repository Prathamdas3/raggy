import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_DIR = BASE_DIR / "temp"


@dataclass
class Configs:
    temp_dir: Path = TEMP_DIR
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


config = Configs()
