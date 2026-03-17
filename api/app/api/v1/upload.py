from fastapi import APIRouter, status, UploadFile, File, HTTPException, Depends
from app.core import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models import Response, FileMeta, Status
from app.utils import save_file
from app.services import get_docs_service, DocsService
from app.api.v1.auth import get_user_id, RefreshTokenUserId
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Qdrant


upload_router = APIRouter(prefix="/upload")
logger = get_logger()

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)


@upload_router.post(
    "/files", status_code=status.HTTP_202_ACCEPTED, response_model=Response
)
def upload_file(
    file: UploadFile = File(...),
    docs_services: DocsService = Depends(get_docs_service),
    user: RefreshTokenUserId = Depends(get_user_id),
):
    try:
        meta = FileMeta.from_upload(file=file)
        file_path = save_file(file=file, file_type=meta.category)
        if not file_path:
            logger.error("Failed to upload the file missing file path", exc_info=True)
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload to file",
            )

        doc_id = docs_services.create_docs(user_id=user.user_id)

        return {
            "message": "Successfully saved the docs",
            "status": Status.success,
            "data": doc_id,
        }
        # loader = PyPDFLoader(file_path=file_path)
        # documents = loader.load()
        # chunks = text_spliter.split_documents(documents=documents)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to file",
        )
