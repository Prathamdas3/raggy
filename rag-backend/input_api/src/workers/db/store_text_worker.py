from lib.pydentic_models import ChunkData
from utils.response import APIError
from lib.celery import celery
from lib.logger import get_logger
from db.store_text import store_original_text
from typing import Dict,List

logger = get_logger("workers/db/store_text")


@celery.task(bind=True)
def send_chunks_to_docs_api_task(self, chat_id:str,user_id:str,chunks:List[ChunkData]) -> Dict:
    """
    Celery task to send chunks to docs API.

    Args:
        user_id: User ID
        chat_id: Chat ID
        chunks: List of chunk dictionaries

    Returns:
        dict: Task result
    """

    import asyncio

    logger.info(f"Celery task started: send_chunks_to_docs_api_task")

    try:
        result = asyncio.run(store_original_text(user_id=user_id,chat_id=chat_id,chunks=chunks))

        logger.info("Chunks sent to docs API successfully")
        return {
            "status": "success",
            "message": "Chunks sent to docs API successfully",
            "code": 200,
            "data": result.get("data"),
        }

    except APIError as ae:
        logger.error(f"Failed to send chunks: {ae.message}")
        return {
            "status": "error",
            "message": ae.message,
            "code": ae.status_code,
            "data": None,
        }

    except Exception as e:
        logger.exception(f"Unexpected error in send_chunks_to_docs_api_task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error sending chunks to docs API",
            "code": 500,
            "data": None,
        }
