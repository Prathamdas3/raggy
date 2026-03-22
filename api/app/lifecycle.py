from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core import get_logger,minio_client,qdrant_store,ai_model

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    try:
        minio_client.initialize()
        logger.info("✓ MinIO ready.")
    except Exception as e:
        logger.error(f"✗ MinIO init failed: {e}")
        raise

    try:
        qdrant_store.get_store()
        logger.info("✓ Qdrant ready.")
    except Exception as e:
        logger.error(f"✗ Qdrant init failed: {e}")
        raise

    try:
        ai_model.initialize()
        logger.info("✓ AI model ready.")
    except Exception as e:
        logger.error(f"✗ AI model init failed: {e}")
        raise

    yield

    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("Shutting down...")
    minio_client.reset()
    qdrant_store.reset()
    ai_model.reset()
    logger.info("✓ Cleanup complete.")

