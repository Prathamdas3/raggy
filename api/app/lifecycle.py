from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("stating up the server events")
    yield
    logger.info("server shutting down")
