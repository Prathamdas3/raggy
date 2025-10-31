from utils.response import APIError
from lib.celery import celery
from lib.logger import get_logger
from dotenv import load_dotenv
import httpx
import os
load_dotenv()
SUMMARY_API_URL=os.getenv("SUMMARY_API_URL")
SUMMARY_API_TIMEOUT=os.getenv("SUMMARY_API_TIMEOUT","100")

logger = get_logger("workers/db/summary_generate")

async def request_summary_generation(user_id:str,chat_id:str,summary:str):
    try:
        async with httpx.AsyncClient(timeout=int(SUMMARY_API_TIMEOUT)) as client:
            payload={
            "user_id":user_id,
            "chat_id":chat_id,
            "original_text":summary
            }
            url=f"{SUMMARY_API_URL}/summary"
            response = await client.post(url,json=payload,headers={"Content-Type":"application/json"})
            logger.info(f"Summary API responded with status code: {response.status_code}")
            if response.status_code == 202:
                logger.info("Summary generation request accepted (202 Accepted)")
                return {
                    "status":"success",
                    "message":"Summary generation request accepted",
                    "code":202,
                    "data":response.json()
                }

            elif response.status_code >=400:
                error_detail = response.text
                logger.error(f"Summary API error ({response.status_code}): {error_detail}")

                raise APIError(
                    f"Summary API error: {response.status_code}",
                    status_code=response.status_code,
                    details=error_detail
                )
            else:
                logger.warning(f"Unexpected status code from Summary API: {response.status_code}")
                return {
                    "status":"success",
                    "message":f"Summary API responded with status {response.status_code}",
                    "code":response.status_code,
                    "data":response.json() if response.text else {}
                }
    except httpx.TimeoutException:
        logger.error(f"Request to Summary API timed out after {SUMMARY_API_TIMEOUT} seconds")
        raise APIError(
            "Summary API request timed out",
            status_code=504,
            details="The request to the Summary API exceeded the timeout limit."
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
def send_request_for_summary_generation(self,user_id:str,chat_id:str,summary:str):
    try:
        if not user_id or not chat_id or not summary:
            logger.error("Missing required parameters for summary generation request")
            return {
                "status":"error",
                "message":"user_id, chat_id, and summary are required parameters",
                "code":400,
                "data":"Missing the chat_id, user_id or summary"
            } 
        import asyncio
        logger.info(f"Initiating summary generation request for user_id: {user_id}, chat_id: {chat_id}")
        response=asyncio.run(request_summary_generation(user_id,chat_id,summary))
        logger.info(f"Summary generation request completed with response: {response}")
        return {
            "status":"success",
            "message":"Summary generation request processed",
            "data":response
        }
    except APIError as api_err:
        logger.error(f"APIError while requesting summary generation: {str(api_err)}")
        return {
            "status":"error",
            "message":"Failed to request summary generation",
            "code":api_err.status_code,
            "data":api_err.details
        }
    except Exception as e:
        logger.error(f"Unexpected error in summary generation request: {str(e)}")
        return {
            "status":"error",
            "message":"An unexpected error occurred",
            "code":500,
            "data":str(e)
        }   


