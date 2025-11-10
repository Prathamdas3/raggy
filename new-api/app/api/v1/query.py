from fastapi import APIRouter, status, HTTPException, Depends
from app.utils.logger import get_logger
from app.schemas.db.message import CreateMessage
from app.services.auth.token import get_user_id_from_access_token
from uuid import UUID

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query", status_code=status.HTTP_202_ACCEPTED)
def ask_question(
    data: CreateMessage, user_id: UUID = Depends(get_user_id_from_access_token)
):
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to upload the query for answer generation: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload the question for answer generation",
        )


@router.get("/{chat_id}/query/{question_id}")
def get_answer(
    question_id: UUID,
    chat_id: UUID,
    user: UUID = Depends(get_user_id_from_access_token),
):
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get the answer for the question with the question_id:{question_id}, error:{str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the answer the for the question with the id",
        )
