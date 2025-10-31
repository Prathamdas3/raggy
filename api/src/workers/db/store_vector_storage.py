from typing import List
from lib.pydentic import ChunkData
from utils.response import APIError
from lib.celery import celery
from lib.logger import get_logger
from dotenv import load_dotenv
import httpx
import os

load_dotenv()
SUMMARY_API_URL = os.getenv("SUMMARY_API_URL")
SUMMARY_API_TIMEOUT = os.getenv("SUMMARY_API_TIMEOUT", "100")
logger = get_logger("workers/db/store_vector_storage")

async def request_vectorstore(chunks:List[ChunkData]):
    try:
        async with httpx.AsyncClient(timeout=int(SUMMARY_API_TIMEOUT)) as client:
            payload={
            "chunks":[chunk.dict() for chunk in chunks]
            }
            url=f"{SUMMARY_API_URL}/save"
            response = await client.post(url,json=payload,headers={"Content-Type":"application/json"})
            logger.info(f"Vector Store API responded with status code: {response.status_code}")
            if response.status_code == 202:
                logger.info("Vector Store request accepted (202 Accepted)")
                return {
                    "status":"success",
                    "message":"Vector Store request accepted",
                    "code":202,
                    "data":response.json()
                }

            elif response.status_code >=400:
                error_detail = response.text
                logger.error(f"Vector Store API error ({response.status_code}): {error_detail}")

                raise APIError(
                    f"Vector Store API error: {response.status_code}",
                    status_code=response.status_code,
                    details=error_detail
                )
            else:
                logger.warning(f"Unexpected status code from Vector Store API: {response.status_code}")
                return {
                    "status":"success",
                    "message":f"Vector Store API responded with status {response.status_code}",
                    "code":response.status_code,
                    "data":response.json() if response.text else {}
                }
    except httpx.TimeoutException:
        logger.error(f"Request to Vector Store API timed out after {SUMMARY_API_TIMEOUT} seconds")
        raise APIError(
            "Vector Store API request timed out",
            status_code=504,
            details="The request to the Vector Store API exceeded the timeout limit."
        )
    except httpx.ConnectError as ce:
        logger.error(f"Failed to connect to Vector Store API: {str(ce)}")
        raise APIError(
            "Failed to connect to Vector Store API",
            status_code=503,
            details=str(ce)
        )
    except Exception as e:
        logger.exception(f"Unexpected error while requesting Vector Store API: {str(e)}")
        raise APIError(
            "Unexpected error while requesting Vector Store API",
            status_code=500,
            details=str(e)
        )
    

@celery.task(bind=True)
def save_chunks_to_vectorstore(self, chunks:List[ChunkData]):
    try: 
        chunks = [ChunkData.model_validate(chunk) for chunk in chunks]
        logger.info(f"Initiating vector store save for {len(chunks)} chunks")
        import asyncio
        logger.info("Sending request to Vector Store API")
        response=asyncio.run(request_vectorstore(chunks))
        logger.info(f"Vector store save request completed with response: {response}")
        return {
            "status":"success",
            "message":"Vector store save request processed",
            "data":response
        }
    except APIError as api_err:
        logger.error(f"APIError while saving chunks to vector store: {str(api_err)}")
        return {
            "status":"error",
            "message":"Failed to save chunks to vector store",
            "code":api_err.status_code,
            "data":api_err.details
        }
    except Exception as e:
        logger.error(f"Unexpected error in save_chunks_to_vectorstore task: {str(e)}")
        return {
            "status":"error",
            "message":"An unexpected error occurred",
            "code":500,
            "data":str(e)
        }

        
