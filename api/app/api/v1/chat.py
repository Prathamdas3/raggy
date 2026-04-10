"""Chat API endpoints.

Provides endpoints for managing chat conversations, including
creating, updating, sharing, and branching conversations.
"""

from fastapi import APIRouter, status, File, UploadFile
from app.utils import CurrentUserDep, validate_and_read, save_bytes_to_minio
from app.core import get_logger, AppException
from app.models import Response, UpdateChat, FileMeta
from app.services import ChatServiceDep
from app.queues.chains import chain_summary
from uuid import UUID

chat_router = APIRouter(prefix="/chat", tags=["chats"])
logger = get_logger(__name__)


# route
@chat_router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=Response)
def create_chat(
    chat_services: ChatServiceDep,
    user: CurrentUserDep,
    file: UploadFile = File(...),
):
    contents = validate_and_read(file)  # read once
    meta = FileMeta.from_upload(file)
    original_doc = save_bytes_to_minio(file, contents,filename=meta.filename,content_type=meta.content_type)  # reuse bytes

    if not original_doc:
        raise AppException(status_code=500, message="Failed to upload file")

    chat_id = chat_services.create_chat(
        user_id=user.user_id,
        title=meta.filename,
        original_doc=original_doc,
    )
    chain_summary(
        {
            "chat_id": str(chat_id),
            "storage_key": original_doc,
            "file_type": meta.category,
            "user_id":str(user.user_id)
        }
    )
    return {"data": chat_id}


@chat_router.get("/", response_model=Response, status_code=status.HTTP_200_OK)
def get_chats(user: CurrentUserDep, chat: ChatServiceDep):
    return {"data": chat.get_chats(user_id=user.user_id)}


@chat_router.get("/{chat_id}", response_model=Response, status_code=status.HTTP_200_OK)
def get_chat(chat_id: UUID, user: CurrentUserDep, chat: ChatServiceDep):
    return {"data": chat.find_chat(chat_id=chat_id, user_id=user.user_id)}


@chat_router.delete(
    "/{chat_id}", response_model=Response, status_code=status.HTTP_200_OK
)
def remove_chat(chat_id: UUID, user: CurrentUserDep, chat: ChatServiceDep):
    return {"data": chat.remove_chat(chat_id=chat_id, user_id=user.user_id)}


@chat_router.patch(
    "/{chat_id}", status_code=status.HTTP_200_OK, response_model=Response
)
def bookmark_chat(
    chat_id: UUID, is_bookmarked: bool, user: CurrentUserDep, chat: ChatServiceDep
):
    data = UpdateChat(
        chat_id=chat_id, user_id=user.user_id, is_bookmarked=is_bookmarked
    )
    return {"data": chat.update_chat(data)}


# @chat_router.get(
#     "/{chat_id}", status_code=status.HTTP_200_OK, response_model=Response
# )
# def get_share_chat(chat_id: UUID, user: CurrentUserDep, chat: ChatServiceDep):
#     return {"data": chat.share_chat(chat_id=chat_id, user_id=user.user_id)}
