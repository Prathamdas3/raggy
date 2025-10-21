import os
from lib.pydentic_models import ChunkData
from utils.response import APIError
from lib.logger import get_logger
from typing import Dict,List
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("db/store-text")

DOCS_API_URL = os.getenv("DOCS_API_URL")
DOCS_API_TIMEOUT = int(os.getenv("DOCS_API_TIMEOUT"))

logger.info(f"Docs API URL: {DOCS_API_URL}")


async def store_original_text(user_id:str,chat_id:str,chunks:List[ChunkData]) -> Dict:
    """
    Send extracted text chunks to the docs API endpoint.

    Args:
        user_id: User ID
        chat_id: Chat ID
        chunks: List of chunk dictionaries with content and metadata

    Returns:
        dict: Response from docs API

    Raises:
        APIError: If request fails
    """
 
    logger.info(
        f"Preparing to send chunks to docs API. User: {user_id}, Chat: {chat_id}, Chunks: {len(chunks)}"
    )
    try:
        # ===== Input Validation =====
        if not user_id:
            logger.error("User ID not provided")
            raise APIError("User ID is required", status_code=400)

        if not chat_id:
            logger.error("Chat ID not provided")
            raise APIError("Chat ID is required", status_code=400)

        if not chunks:
            logger.error("No chunks provided")
            raise APIError("Chunks list cannot be empty", status_code=400)

        if not isinstance(chunks, list):
            logger.error(f"Chunks must be a list, received: {type(chunks)}")
            raise APIError("Chunks must be a list", status_code=400)

        # ===== Validate Chunk Structure =====
        for idx, chunk in enumerate(chunks):
            if not isinstance(chunk, dict):
                logger.error(f"Chunk {idx} is not a dictionary")
                raise APIError(f"Chunk {idx} must be a dictionary", status_code=400)

            if "content" not in chunk:
                logger.error(f"Chunk {idx} missing 'content' field")
                raise APIError(f"Chunk {idx} missing 'content' field", status_code=400)

            if "metadata" not in chunk:
                logger.error(f"Chunk {idx} missing 'metadata' field")
                raise APIError(f"Chunk {idx} missing 'metadata' field", status_code=400)

            metadata = chunk["metadata"]
            required_fields = ["user_id", "chat_id", "chunk_index"]
            for field in required_fields:
                if field not in metadata:
                    logger.error(f"Chunk {idx} metadata missing '{field}' field")
                    raise APIError(
                        f"Chunk {idx} metadata missing '{field}' field", status_code=400
                    )

        # ===== Prepare Request Data =====
        request_data = {"user_id": user_id, "chat_id": chat_id, "original_text": chunks}

        logger.info(
            f"Request data prepared. Total payload size: {len(str(request_data))} bytes"
        )

        try:
            logger.info(f"Sending request to docs API: {DOCS_API_URL}")
            url=f"{DOCS_API_URL}/docs"
     
            async with httpx.AsyncClient(timeout=DOCS_API_TIMEOUT) as client:
                response = await client.post(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                )

                logger.info(
                    f"Docs API responded with status code: {response.status_code}"
                )

                # ===== Handle Response =====
                if response.status_code == 201:
                    logger.info("Chunks accepted by docs API (201 Created)")
                    return {
                        "status": "success",
                        "message": "Chunks created in docs API",
                        "code": 201,
                        "data": response.json(),
                    }

                elif response.status_code >= 400:
                    error_detail = response.text
                    logger.error(
                        f"Docs API error ({response.status_code}): {error_detail}"
                    )

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
            logger.error(
                f"Request to docs API timed out after {DOCS_API_TIMEOUT} seconds"
            )
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

        except Exception as e:
            logger.exception(f"Unexpected error sending request to docs API: {str(e)}")
            raise APIError(
                "Unexpected error communicating with docs API",
                status_code=500,
                details=str(e),
            )

    except APIError:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error in send_chunks_to_docs_api: {str(e)}")
        raise APIError(
            "Unexpected error sending chunks to docs API",
            status_code=500,
            details=str(e),
        )
