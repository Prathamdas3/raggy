from db.index import SessionDep
from lib.logger import get_logger
from db.schema import Chats
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status, Query
from typing import Annotated, Optional
from sqlmodel import select
from pydantic import BaseModel,field_validator
import uuid

logger = get_logger("db/queries/chat")


class UpdateChat(BaseModel):
    chat_name: Optional[str] = None
    is_bookmarked: Optional[bool] = None

    @field_validator('chat_name')
    @classmethod
    def validate_chat_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate chat name is not empty or just whitespace."""
        if v is not None and not v.strip():
            raise ValueError("Chat name cannot be empty or just whitespace")
        return v.strip() if v else v


    class Config:
        exclude_unset = True


def create_chat(chat: Chats, session: SessionDep) -> Chats:
    try:
        logger.info("Creating new chat")

        session.add(chat)
        session.commit()
        session.refresh(chat)

        logger.info(f"Successfully created chat with ID: {chat.id}")
        return chat

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity constraint violation while creating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat already exists or violates database constraints",
        )

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while creating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while creating chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_chats(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[Chats]:
    try:
        logger.info("Getting the chats detail")
        chats = session.exec(select(Chats).offset(offset).limit(limit)).all()
        logger.info("Successfully fetched all the chats from the db")
        return chats

    except SQLAlchemyError as e:
        logger.error(f"Database error while getting chats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while getting chats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_chat_by_id(chat_id: uuid.UUID, session: SessionDep) -> Chats:
    try:
        logger.info(f"Fetching the chat with the id {chat_id}")
        chat = session.get(Chats, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        logger.info(f"Successfully fetched the chat with the chat id:{chat_id}")
        return chat
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while getting chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def delete_chat(chat_id: uuid.UUID, session: SessionDep):
    try:
        logger.info(f"Initating the delete process for the chat id:{chat_id}")
        chat = session.get(Chats, chat_id)
        if not chat:
            logger.error(f"failed to get the chat with id: {chat_id}")
            raise HTTPException(status_code=404, detail="No chat exists with this id")
        session.delete(chat)
        session.commit()
        logger.info("Successfully deleted the chat")
        return {"ok": True}
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while deleting chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while deleting chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def update_chat_name(chat_id: uuid.UUID, chat_update: UpdateChat, session: SessionDep):
    try:
        chat = session.get(Chats, chat_id)
        if not chat:
            logger.error(f"No chat found for the given id:{chat_id}")
            raise HTTPException(
                status_code=404, detail="No chat found for the given id"
            )

        # Get only the fields that were actually set in the request
        update_data = chat_update.model_dump(exclude_unset=True)

        # updateing the chat with the new fileds from the request
        for field, value in update_data.items():
            setattr(chat, field, value)

        session.add(chat)
        session.commit()
        session.refresh(chat)

        logger.info(
            f"Successfully updated chat ID: {chat_id} with fields: {list(update_data.keys())}"
        )
        return chat

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while updating chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
