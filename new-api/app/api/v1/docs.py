from fastapi import APIRouter, status, HTTPException, Depends
from app.utils.logger import get_logger
from app.schemas.db.docs import DocsReq
from app.utils.token import get_user_id_from_access_token

router = APIRouter()
logger = get_logger(__name__)


@router.post("/docs", status_code=status.HTTP_202_ACCEPTED)
def upload_file(data: DocsReq, user_id=Depends(get_user_id_from_access_token)):
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document in the db: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload docs",
        )
