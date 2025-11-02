from lib.logger import get_logger
from lib.celery import celery
from dotenv import load_dotenv
import os
import httpx
from utils.response import APIError

load_dotenv()
logger = get_logger("workers/db/store_audio")

DOCS_API_URL = os.getenv("DOCS_API_URL")
DOCS_API_TIMEOUT = int(os.getenv("DOCS_API_TIMEOUT"))

logger.info(f"Docs API URL: {DOCS_API_URL}")


async def send_patch_request(url, chat_id: str, audio_url: str):
    try:
        async with httpx.AsyncClient(timeout=DOCS_API_TIMEOUT) as client:
            response = await client.patch(
                url,
                json={"chat_id": chat_id, "audio_url": audio_url},
                headers={"Content-Type": "application/json"},
            )

            logger.info(f" API responded with status code: {response.status_code}")
            if response.status_code == 200:
                logger.info("Audio URL accepted by API (200 OK)")
                return {
                    "status": "success",
                    "message": "Audio URL saved in docs API",
                    "code": 200,
                    "data": response.json(),
                }

            elif response.status_code >= 400:
                error_detail = response.text
                logger.error(f"Docs API error ({response.status_code}): {error_detail}")

                raise APIError(
                    f"Docs API error: {response.status_code}",
                    status_code=response.status_code,
                    details=error_detail,
                )
            else:
                logger.warning(
                    f"Unexpected status code from docs API: {response.status_code}"
                )
                return {
                    "status": "success",
                    "message": f"Docs API responded with status {response.status_code}",
                    "code": response.status_code,
                    "data": response.json() if response.text else {},
                }
    except httpx.TimeoutException:
        logger.error(f"Request to docs API timed out after {DOCS_API_TIMEOUT} seconds")
        raise APIError(
            "Docs API request timed out",
            status_code=504,
            details=f"Timeout after {DOCS_API_TIMEOUT} seconds",
        )

    except httpx.ConnectError as ce:
        logger.error(f"Failed to connect to docs API: {str(ce)}")
        raise APIError(
            "Failed to connect to docs API",
            status_code=503,
            details=f"Connection error: {str(ce)}",
        )

    except httpx.RequestError as re:
        logger.error(f"HTTP request error to docs API: {str(re)}")
        raise APIError(
            "HTTP request error",
            status_code=500,
            details=f"Request error: {str(re)}",
        )


@celery.task(bind=True)
def store_audio_to_db(self, chat_id: str, audio_url: str):
    try:
        if not chat_id or not audio_url:
            logger.error("Invalid parameters for store_audio_to_db task")
            return {
                "status": "error",
                "message": "user_id, chat_id, and audio_url are required",
                "code": 400,
                "data": None,
            }

        if audio_url.strip() == "" or chat_id.strip() == "":
            logger.error("Empty parameter after stripping")
            return {
                "status": "error",
                "message": "audio_url cannot be empty",
                "code": 400,
                "data": None,
            }

        logger.info(f"Processing audio URL for chat: {chat_id}")

        try:
            import asyncio

            logger.info(f"Sending audio URL to docs API for storage.  Chat: {chat_id}")
            url = f"{DOCS_API_URL}/docs"
            response = asyncio.run(
                send_patch_request(url, chat_id=chat_id, audio_url=audio_url)
            )
            logger.info("Audio URL successfully sent to docs API")
            return {
                "status": "success",
                "message": "Audio URL stored successfully",
                "code": 200,
                "data": response,
            }
        except APIError as api_err:
            logger.error(
                f"APIError while sending audio URL to docs API: {str(api_err)}"
            )
            return {
                "status": "error",
                "message": f"Failed to store audio URL: {str(api_err)}",
                "code": api_err.status_code,
                "data": None,
            }
    except Exception as e:
        logger.exception(
            f"Unexpected error while sending audio URL to docs API: {str(e)}"
        )
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "code": 500,
            "data": None,
        }
