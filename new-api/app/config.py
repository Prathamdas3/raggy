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
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
    DATABASE_URI = os.getenv("DATABASE_URI", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "")
    HUGGINGFACE_DEVICE = os.getenv("HUGGINGFACE_DEVICE", "cpu")


config = Configs()