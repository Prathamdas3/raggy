from fastapi import APIRouter, status, UploadFile, File, HTTPException
from app.core.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models.file import FileMeta
from app.models import Response
from langchain_community.document_loaders import PyPDFLoader
from app.utils.savefile import save_file
from langchain_community.vectorstores import Qdrant


upload_router = APIRouter(prefix="/upload")
logger = get_logger()

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)


@upload_router.post(
    "/files", status_code=status.HTTP_202_ACCEPTED, response_model=Response
)
def upload_file(file: UploadFile = File(...)):
    try:
        meta = FileMeta.from_upload(file=file)
        file_path = save_file(file=file, file_type=meta.category)
        loader = PyPDFLoader(file_path=file_path)
        documents = loader.load()
        chunks = text_spliter.split_documents(documents=documents)

    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to file",
        )
