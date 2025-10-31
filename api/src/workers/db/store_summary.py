from lib.logger import get_logger
from lib.celery import celery
from dotenv import load_dotenv
import os
import httpx
from utils.response import APIError

load_dotenv()
logger = get_logger("workers/db/store_summary")

DOCS_API_URL = os.getenv("DOCS_API_URL")
DOCS_API_TIMEOUT = int(os.getenv("DOCS_API_TIMEOUT"))

logger.info(f"Docs API URL: {DOCS_API_URL}")


async def send_patch_request(url, chat_id: str, summary_text: str):
    try:
        async with httpx.AsyncClient(timeout=DOCS_API_TIMEOUT) as client:
            response = await client.patch(
                url,
                json={"chat_id": chat_id, "summary_text": summary_text},
                headers={"Content-Type": "application/json"},
            )

            logger.info(f"Docs API responded with status code: {response.status_code}")
            if response.status_code == 200:
                logger.info("Chunks accepted by docs API (200 Created)")
                return {
                    "status": "success",
                    "message": "Chunks created in docs API",
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
def store_summary_to_db(self, user_id: str, chat_id: str, summary: str):
    try:
        if not user_id or not chat_id or not summary:
            logger.error("Invalid parameters for store_summary_to_db task")
            return {
                "status": "error",
                "message": "user_id, chat_id, and summary are required",
                "code": 400,
                "data": None,
            }

        if summary.strip() == "" or chat_id.strip() == "":
            logger.error("Summary text is empty after stripping")
            return {
                "status": "error",
                "message": "summary text or chat_id cannot be empty",
                "code": 400,
                "data": None,
            }

        logger.info(f"Processing summary storing ")

        try:
            import asyncio

            logger.info(
                f"Sending summary to docs API for storage. User: {user_id}, Chat: {chat_id}"
            )
            url = f"{DOCS_API_URL}/docs"
            response = asyncio.run(
                send_patch_request(url, chat_id=chat_id, summary_text=summary)
            )
            logger.info("Summary successfully sent to docs API")
            return {
                "status": "success",
                "message": "Summary stored successfully",
                "code": 200,
                "data": response,
            }
        except APIError as api_err:
            logger.error(f"APIError while sending summary to docs API: {str(api_err)}")
            return {
                "status": "error",
                "message": f"Failed to store summary: {str(api_err)}",
                "code": api_err.status_code,
                "data": None,
            }
    except Exception as e:
        logger.exception(
            f"Unexpected error while sending summary to docs API: {str(e)}"
        )
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "code": 500,
            "data": None,
        }
