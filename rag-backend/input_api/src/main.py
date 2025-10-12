import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, Form
from pydentic_models import SuccessResponse
from utils.response import APIError, api_error_handler
from utils.logger import get_logger
from utils.file import detect_file_type, save_temp_file, cleanup_temp_files
from constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    YT_REGEX,
)

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server events")
    asyncio.create_task(cleanup_temp_files())
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
        file_type = await detect_file_type(file)
        file_path = await save_temp_file(file)

        if file_type in ALLOWED_DOC_TYPES:
            logger.info(
                f"Processing document file: {file.filename} of type {file_type} "
                f"local path {file_path}"
            )
            # await extract_text_from_othertypes.delay(file_path, file_type)

        elif file_type in ALLOWED_IMAGE_TYPES:
            logger.info(
                f"Processing image file: {file.filename} of type {file_type} "
                f"local path {file_path}"
            )
            # add to image queue
            pass

        elif file_type in ALLOWED_AUDIO_TYPES:
            logger.info(
                f"Processing audio file: {file.filename} of type {file_type} "
                f"local path {file_path}"
            )
            # add to audio queue
            pass

        elif file_type in ALLOWED_VIDEO_TYPES:
            logger.info(
                f"Processing video file: {file.filename} of type {file_type} "
                f"local path {file_path}"
            )
            # add to video queue
            pass

        else:
            pass
            # raise APIError("Unsupported file type", status_code=400)

        logger.info(f"File {file.filename} processed as type {file_type}")
        return SuccessResponse(
            data={"filename": file.filename, "file_type": file_type},
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


@api_router.get("/yt")
async def process_youtube_link(link: str, user_id: str, chat_id: str):
    logger.info(f"Processing YouTube link: {link}")

    if not YT_REGEX.match(link):
        logger.error(f"Invalid YouTube link: {link}")
        raise APIError("Invalid YouTube link", status_code=400)

    logger.success(f"YouTube link {link} processed successfully")
    return SuccessResponse(
        data={"link": link},
        status="accepted",
        message="YouTube link processed successfully",
    )


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
