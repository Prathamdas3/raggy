import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, Form
from lib.pydentic_models import YTRequestModel
from workers.yt import extract_text_from_yt_link
from lib.whisper import get_whisper_model
from lib.pydentic_models import SuccessResponse
from utils.response import APIError, api_error_handler
from lib.logger import get_logger
from utils.files.file import handle_file
from utils.files.clean import cleanup_temp_files
from constants import (
    YT_REGEX,
)

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server events")
    asyncio.create_task(cleanup_temp_files())
    get_whisper_model("base")
    yield
    logger.info("Shutting down the server events")


app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")
app.add_exception_handler(APIError, api_error_handler)


@api_router.get("/")
async def check():
    return {"status": "ok"}


@api_router.post("/file", status_code=202)
async def upload_file(
    chat_id: str = Form(...), user_id: str = Form(...), file: UploadFile = File(...)
):
    logger.info(f"Received file: {file.filename}")

    try:
        await handle_file(file=file,chat_id=chat_id,user_id=user_id)
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


@api_router.post("/yt", status_code=200)
async def process_youtube_link(req: YTRequestModel):
    logger.info(f"Processing YouTube link: {req.link}")

    if not YT_REGEX.match(req.link):
        logger.error(f"Invalid YouTube link: {req.link}")
        raise APIError("Invalid YouTube link", status_code=400)

    try:
        logger.info(f"Queuing YouTube link for processing: {req.link}")
        task = extract_text_from_yt_link.delay(link=req.link,chat_id=req.chat_id,user_id=req.user_id)
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


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
