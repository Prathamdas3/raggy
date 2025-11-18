from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends, Form
from app.configs.rate_limiter import rate_limit_default
from app.schemas.db.docs import DocsReqLink
from app.schemas.input.file import FileMeta, OtherInput
from app.schemas.input.yt import YTInput
from app.utils.logger import get_logger
from app.configs.database import SessionDep
from uuid import UUID
from app.services.db.chat import (
    create_chat,
    get_chats,
    update_chat as update_chat_fn,
    remove_chat,
    get_summary as get_chat_summary,
    get_chat_messages,
)
from app.services.auth.token import get_user_id_from_access_token
from app.schemas.response import Response as ReturnResponse
from app.schemas.db.chat import GetSummary, UpdateChat
from app.tasks.chains import chain_input_link, chain_input_others
from app.utils.save_file import save_file

router = APIRouter(prefix="/chats")

logger = get_logger(__name__)


@router.post(
    "/links", status_code=status.HTTP_201_CREATED, dependencies=[rate_limit_default()]
)
def create_new_links_chat(
    session: SessionDep,
    link: str | None = Form(None),
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    data = DocsReqLink(link=link)
    try:
        logger.debug("Starting the process of creating a chat")
        new_id = create_chat(user_id=UUID(str(user_id)), session=session)

        if not new_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No chat created ",
            )

        details = YTInput(
            user_id=user_id,
            chat_id=new_id,
            link=data.link,
        )
        chain_input_link(data=details)

        return ReturnResponse(status="success", message="Successfully created the chat")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while chat creation",
        )


@router.post(
    "/files", status_code=status.HTTP_202_ACCEPTED, dependencies=[rate_limit_default()]
)
def create_new_files_chat(
    session: SessionDep,
    file: UploadFile | None = File(None),
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug("Starting the process of creating a chat")
        new_id = create_chat(user_id=UUID(str(user_id)), session=session)

        if not new_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No chat created ",
            )

        meta = FileMeta.from_upload(file)
        final_path = save_file(file_type=meta.category, file=file)

        details = OtherInput(
            user_id=user_id,
            chat_id=new_id,
            path=final_path,
            sub_type=meta.subtype,
            type=meta.category,
        )

        chain_input_others(details)

        return ReturnResponse(status="success", message="Successfully created the chat")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create the chat, {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while chat creation",
        )


@router.get("/", status_code=status.HTTP_200_OK, dependencies=[rate_limit_default()])
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


@router.patch(
    "/{chat_id}", status_code=status.HTTP_200_OK, dependencies=[rate_limit_default()]
)
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
        chat = update_chat_fn(session=session, details=details, chat_id=chat_id)
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


@router.delete(
    "/{chat_id}", status_code=status.HTTP_200_OK, dependencies=[rate_limit_default()]
)
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


@router.get(
    "/{chat_id}/summary",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def get_summary(
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug(f"Started to fetch the summary for the chat_id:{chat_id}")

        get_summary_args = GetSummary(user_id=user_id, chat_id=chat_id)
        data = get_chat_summary(session=session, details=get_summary_args)

        logger.debug("Successfully fetched the summary for the docs")
        return ReturnResponse(
            status="success",
            message="successfully fetched the summary",
            data=data,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get the summary for the chat: {str(e)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the summary for the chat",
        )


@router.get(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def get_chats_message(
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug(f"Fetching all the messages in the chat with the id: {chat_id}")
        args = GetSummary(user_id=user_id, chat_id=chat_id)
        messages = get_chat_messages(details=args, session=session)
        logger.debug(
            f"Successfully fetched all the messages for the chat with the id: {chat_id}"
        )
        return ReturnResponse(
            status="success",
            message="Successfully fetched all the messages of the chat",
            data=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to fetch all the messages for the chat: {str(e)}", exc_info=True
        )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the audio of summary for the chat",
        )
