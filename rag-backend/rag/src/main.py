from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from lib.pydentic import QuestionRequest, SendChunksRequest, SuccessResponse, SummaryRequest
from lib.logger import get_logger
from utils.response import APIError, api_error_handler

load_dotenv()
logger = get_logger("main")

app = FastAPI()
api_router = APIRouter(prefix="/api")
app.add_exception_handler(APIError, api_error_handler)


@api_router.get("/")
async def check():
    return {"status": "ok"}


@api_router.post("/v1/summary", status_code=202)
async def create_summary(data: SummaryRequest):
    try: 
        if not data:
            logger.error("No data provided for summary")
            raise APIError("No data provided for summary",status_code=400)
        
        if not isinstance(data,SummaryRequest):
            logger.error("Invalid data format for summary")
            raise APIError("Invalid data format for summary",status_code=400)
        
        user_id = data.user_id
        chat_id = data.chat_id
        original_text = data.original_text
        if not user_id:
            logger.error("user_id is empty")
            raise APIError("user_id cannot be empty",status_code=400)
        if not chat_id:
            logger.error("chat_id is empty")
            raise APIError("chat_id cannot be empty",status_code=400)
        if not original_text or len(original_text) == 0:
            logger.error("original_text is empty")
            raise APIError("original_text cannot be empty",status_code=400)
        
        from workers.summary import generate_summary_task
        logger.info(f"Submitting summary generation task for user: {user_id}, chat: {chat_id}")
        task = generate_summary_task.delay(original_text=original_text,user_id=user_id,chat_id=chat_id)

        logger.info(f"Summary generation task submitted with task ID: {task.id}")
        return SuccessResponse(
            data={"task_id": task.id},
            status="accepted",
            message="Summary generation task submitted successfully",
        )
    except APIError:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in create_summary endpoint: {str(e)}")
        raise APIError(f"Unexpected error during summary creation: {str(e)}",status_code=500)



@api_router.post("/v1/save", status_code=202)
async def save_to_qdrant(data: SendChunksRequest):
    pass


@api_router.post("/v1/generate-answer", status_code=202)
async def create_question_to_answer(data: QuestionRequest):
    # create summary of the original text
    # create audio of the summary text
    # save both the audio and summary to the db
    pass

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server on port 8300")
    uvicorn.run(app, host="0.0.0.0", port=8300,reload=True)
