from fastapi import APIRouter, status, UploadFile, File, HTTPException
from app.core.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models.response import Response
from app.core.config import config

upload_router = APIRouter(prefix="/upload")
logger = get_logger()

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)


@upload_router.post("/files", status_code=status.HTTP_202_ACCEPTED,response_model=Response)
def upload_file(file: UploadFile | None = File(None)):
    try:
        config.temp_dir.mkdir(parents=True, exist_ok=True)


    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to file",
        )
