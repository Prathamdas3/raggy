import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, Form
from lib.pydentic import QuestionRequest, YTRequestModel
from workers.input.yt import extract_text_from_yt_link
from lib.whisper import get_whisper_model
from lib.pydentic import SuccessResponse
from lib.model import get_model
from lib.minio import initialize_minio
from lib.qdrant import initialize_qdrant
from utils.response import APIError, api_error_handler
from lib.logger import get_logger
from utils.files.file import handle_file
from utils.files.clean import cleanup_temp_files
from db.index import create_db_and_tables
import db.schema as schema
from constants import (
    YT_REGEX,
)
from dotenv import load_dotenv

load_dotenv()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server events")
    cleanup_task = asyncio.create_task(cleanup_temp_files())
    try:
        logger.info("Pre-loading Whisper model...")
        # Run model loading in thread to avoid blocking
        await asyncio.to_thread(get_whisper_model, "base")
        logger.info("Whisper model pre-loaded successfully")
    except Exception as e:
        logger.error(f"Failed to pre-load Whisper model: {str(e)}")
        logger.warning("Whisper model will be lazy-loaded on first use")

    try:
        logger.info("Pre-loading HuggingFace model...")
        # Run model loading in thread to avoid blocking
        await asyncio.to_thread(get_model)
        logger.info("Model pre-loaded successfully")
    except Exception as e:
        logger.error(f"Failed to pre-load model: {str(e)}")
        logger.warning("Model will be lazy-loaded on first use")

    logger.info("🚀 Starting up FastAPI application...")
    try:
        initialize_minio()
        logger.info("✓ MinIO initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize MinIO: {e}")

    logger.info("Vector initialization Starting...")
    try:
        initialize_qdrant()
        logger.info("✓ Qdrant initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Qdrant: {e}")

    try:
        create_db_and_tables()
        logger.info("Successfully created the db tables")
    except Exception as e:
        logger.error(f"Failed to create the db tables {e}")

    yield
    # ===== Shutdown =====
    logger.info("Shutting down the server...")

    # Cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Cleanup task cancelled")

    logger.info("Server shutdown complete")


app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")
app.add_exception_handler(APIError, api_error_handler)


@api_router.get("/")
async def check():
    return {"status": "ok"}


@api_router.post("/v1/file", status_code=202)
async def upload_file(
    chat_id: str = Form(...), user_id: str = Form(...), file: UploadFile = File(...)
):
    logger.info(f"Received file: {file.filename}")

    try:
        await handle_file(file=file, chat_id=chat_id, user_id=user_id)
        logger.info(f"File {file.filename} processed successfully")
        return SuccessResponse(
            data={"filename": file.filename},
            status="accepted",
            message="File processed successfully",
        )

    except ValueError as ve:
        logger.error(f"Validation error saving file {file.filename}: {ve}")
        raise APIError(str(ve), status_code=400)

    except RuntimeError as re:
        logger.error(f"Failed to save file {file.filename}: {re}")
        raise APIError("Failed to save file", status_code=500, details=str(re))

    except HTTPException as e:
        logger.error(f"HTTP error processing file {file.filename}: {e.detail}")
        raise APIError(e.detail, status_code=e.status_code)

    except APIError:
        # Re-raise APIError exceptions to be handled by the exception handler
        raise

    except Exception as e:
        logger.error(f"Unexpected error processing file {file.filename}: {str(e)}")
        raise APIError("Unexpected server error", status_code=500, details=str(e))


@api_router.post("/v1/yt", status_code=200)
async def process_youtube_link(req: YTRequestModel):
    logger.info(f"Processing YouTube link: {req.link}")

    if not YT_REGEX.match(req.link):
        logger.error(f"Invalid YouTube link: {req.link}")
        raise APIError("Invalid YouTube link", status_code=400)

    try:
        logger.info(f"Queuing YouTube link for processing: {req.link}")
        task = extract_text_from_yt_link.delay(
            link=req.link, chat_id=req.chat_id, user_id=req.user_id
        )
        logger.info(f"Queued YouTube link task {task.id} for processing: {req.link}")

        logger.info(f"YouTube link {req.link} processed successfully")
        return SuccessResponse(
            data={"link": req.link},
            status="accepted",
            message="YouTube link processed successfully",
        )
    except Exception as e:
        logger.error(
            f"Failed to queue YouTube link {req.link} for processing: {str(e)}"
        )
        raise APIError(
            "Failed to queue YouTube link for processing",
            status_code=500,
            details=str(e),
        )


@api_router.post("/v1/generate-answer", status_code=202)
async def create_question_to_answer(data: QuestionRequest):
    try:
        if not data:
            logger.error("No data provided for answer generation")
            raise APIError("No data provided", status_code=400)
        if not isinstance(data, QuestionRequest):
            logger.error("Invalid data format for answer generation")
            raise APIError("Invalid data fromat for answer generation", status_code=400)

        question = data.question
        user_id = data.user_id
        chat_id = data.chat_id
        question_id = data.question_id

        if not user_id or user_id.strip() == "":
            logger.error("user_id is empty")
            raise APIError("user_id cannot be empty", status_code=400)

        if not chat_id or chat_id.strip() == "":
            logger.error("chat_id is empty")
            raise APIError("chat_id can not be empty", status_code=400)

        if not question_id or question_id.strip() == "":
            logger.error("question_id is empty")
            raise APIError("question_id can not be empty", status_code=400)

        if not question or question.strip() == "":
            logger.error("question is empty")
            raise APIError("question can not be empty", status_code=400)

        logger.info(
            f"Sumitting answer generation for the question_id:{question_id} and the question is {question}"
        )
        try:
            from workers.rag.query import handle_query

            print(len(question))
            response = handle_query.delay(
                user_id=user_id,
                chat_id=chat_id,
                question=question,
                question_id=question_id,
            )

            logger.info("Submited for answer generation queue")
            return SuccessResponse(
                data={"task_id": response.id},
                status="accepted",
                message="answer generation task submitted successfully",
            )
        except Exception as e:
            raise APIError(
                f"Failed to load the data into the queue: {str(e)}", status_code=500
            )

    except APIError:
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error in create_question_to_answer endpoint: {str(e)}"
        )
        raise APIError(
            f"Unexpected error during answer generation: {str(e)}", status_code=500
        )


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
