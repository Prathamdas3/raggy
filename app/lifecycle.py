from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import get_logger
from app.core.config import config
import os

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("stating up the server events")
    if not os.path.exists(config.temp_dir):
        os.makedirs(config.temp_dir)
    yield
    logger.info("server shutting down")
