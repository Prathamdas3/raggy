from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.configs.rate_limiter import rate_limit_default
from app.services.auth.token import get_user_id_from_access_token
from app.services.db.chat import get_chat_share_id
from app.utils.logger import get_logger
from app.configs.database import SessionDep
from app.schemas.response import Response as ReturnResponse

router = APIRouter(prefix="/share")

logger = get_logger(__name__)


@router.get(
    "/{share_id}", status_code=status.HTTP_200_OK, dependencies=[rate_limit_default()]
)
def create_fork_chat(
    session: SessionDep,
    share_id: str,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug("Creating fork chat from the share_id")
        chat_id = get_chat_share_id(share_id=share_id, new_user_id=user_id, session=session)

        if not chat_id:
            raise HTTPException(
                detail="Failed to retrive the chat from the share id",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return ReturnResponse(
            status="success",
            message="Successfully forked the chat",
            data={"chat_id": chat_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fork the chat, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error whiel chat forking",
        )
