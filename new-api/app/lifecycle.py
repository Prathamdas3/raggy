from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.logger import get_logger
from app.configs import database,whisper
import asyncio

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server events")
    try:
        logger.info("starting db connection")
        database.init_db()
        logger.info("db setup done")
    except Exception:
        raise

    try:
        logger.info("starting the whisper ai connection")
        await asyncio.to_thread(whisper.get_whisper_model,"base")
        logger.info("Whisper model pre loaded successfully")
    except Exception:
        raise

    
        

    yield

    logger.info("Server shutdown complete")
