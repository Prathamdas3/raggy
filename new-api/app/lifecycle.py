from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.logger import get_logger
from app.configs.database import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server events")
    init_db()

    yield

    logger.info("Server shutdown complete")
