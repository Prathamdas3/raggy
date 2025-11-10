from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.logger import get_logger
from app.configs.database import SessionDep
from uuid import UUID
from app.services.db.chat import (
    create_chat,
    get_chats,
    update_chat as update_chat_fn,
    remove_chat,
    get_summary as get_chat_summary,
)
from app.services.auth.token import get_user_id_from_access_token
from app.schemas.response import Response as ReturnResponse
from app.schemas.db.chat import UpdateChat

router = APIRouter(prefix="/chats")

logger = get_logger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_chat(
    session: SessionDep, user_id: UUID = Depends(get_user_id_from_access_token)
):
    try:
        logger.debug("Starting the process of creating a chat")
        new_id = create_chat(user_id=UUID(str(user_id)), session=session)

        if not new_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No chat created ",
            )

        logger.debug(f"Successfully created the chat with the id {new_id}")
        return ReturnResponse(status="success", message="Successfully created the chat")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while chat creation",
        )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_chats(
    session: SessionDep, user_id: UUID = Depends(get_user_id_from_access_token)
):
    try:
        logger.debug(f"Started to get the chats with the user_id:{user_id}")
        chats = get_chats(user_id=UUID(str(user_id)), session=session)
        logger.debug(
            f"Successfully fetched all the chats with the user_id:{user_id}, len: {len(chats)}"
        )
        return ReturnResponse(
            message="Successfully fetched all the chats", status="success", data=chats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get all the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching all the chats",
        )


@router.patch("/{chat_id}", status_code=status.HTTP_200_OK)
def update_chat(
    chat_id: UUID,
    session: SessionDep,
    details: UpdateChat,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug(
            f"Starting to update the chat with the user_id:{user_id} and chat_id:{chat_id}"
        )
        chat = update_chat_fn(
            chat_id=UUID(str(chat_id)),
            user_id=UUID(str(user_id)),
            session=session,
            details=details,
        )
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update the chat",
            )
        logger.debug(f"updated the chat successfully with the id:{chat}")
        return ReturnResponse(message="Successfully updated the chat", status="success")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to updating the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating the chat",
        )


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
def delete_chat(
    session: SessionDep,
    chat_id: UUID,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug(
            f"Strating to remove the chat withe the chat_id: {chat_id}, user_id: {user_id}"
        )

        remove_chat(
            session=session, chat_id=UUID(str(chat_id)), user_id=UUID(str(user_id))
        )

        logger.debug("Successfully removed the chat")
        return ReturnResponse(message="Successfully removed the chat", status="success")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to remove the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while removing the chat",
        )


@router.get("/{chat_id}/summary", status_code=status.HTTP_200_OK)
def get_summary(
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug(f"Started to fetch the summary for the chat_id:{chat_id}")

        summary = get_chat_summary(session=session, user_id=user_id, chat_id=chat_id)

        logger.debug("Successfully fetched the summary for the docs")
        return ReturnResponse(
            status="Success",
            message="successfully fetched the summary for the summary",
            data={"summary": summary},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get the summary for the chat: {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the summary for the chat",
        )
