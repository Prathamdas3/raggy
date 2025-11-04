from db.index import SessionDep
from lib.logger import get_logger
from db.schema import Chats
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status, Query
from typing import Annotated
from sqlmodel import select
import uuid

logger = get_logger("db/queries/chat")


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
        logger.info("Getting the chats details")
        chats = session.exec(select(Chats).offset(offset).limit(limit)).all()
        logger.info("Successfully fetched all the chats from the db")
        return chats

    except SQLAlchemyError as e:
        logger.error(f"Database error while creating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while creating chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_chat_by_id(chat_id: uuid.UUID, session: SessionDep) -> Chats:
    try:
        logger.info(f"Fetching the chat with the id {chat_id}")
        chat = session.get(Chats, chat_id)
        if not chat:
            raise HTTPException(status_code=404, details="Chat not found")

        logger.info(f"Successfully fetched the chat with the chat id:{chat_id}")
        return chat
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while creating chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def delete_chat(chat_id: uuid.UUID, session: SessionDep):
    try:
        logger.info(f"Initating the delete process for the chat id:{chat_id}")
        chat = session.get(Chats, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="No chat exists with this id")
        session.delete(chat)
        session.commit()
        logger.info("Successfully deleted the chat")
        return {"ok": True}
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


def update_chat_name(chat_id: uuid.UUID, session: SessionDep):
    try:
        chat = session.get(Chats, chat_id)
        if not chat:
            raise HTTPException(
                status_code=404, details="No chat found for the given id"
            )
        pass

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
