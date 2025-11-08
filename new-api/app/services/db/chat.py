from app.models.all_schema import Chats
from fastapi import HTTPException, status
from app.utils.logger import get_logger
from sqlmodel import Session as SessionDep, select
from uuid import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.response import Response
from app.schemas.db.chat import UpdateChat

logger = get_logger(__name__)


def create_chat(
    session: SessionDep, user_id: UUID 
) -> UUID:
    """Creating chat for the user"""
    if not user_id or not isinstance(user_id, UUID):
        raise TypeError("user_id must be an uuid type")
    try:
        logger.debug(f"Starting to create the chat with the user id: {user_id}")
        new_chat = Chats(user_id=user_id, is_bookmarked=False, chat_name=None)
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)
        logger.debug(
            f"chat created successfully for the user id {user_id}, chat id: {new_chat.id}"
        )
        return new_chat.id
    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to create the chat for the user with user id: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while creating the chat: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def get_chats(
    session: SessionDep, user_id: UUID
) -> list[Chats]:
    if not user_id or not isinstance(user_id, UUID):
        raise TypeError("user_id must be an uuid type")

    try:
        logger.debug(f"Started fetching all the chats for the user with id:{user_id}")
        statement = select(Chats).where(Chats.user_id == user_id)
        chats = session.exec(statement=statement).all()

        if not chats:
            return []

        logger.debug("Successfully fetched the chats")
        return chats
    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to fetch all the chats for the user with user id: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while fetching the chats: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def remove_chat(
    session: SessionDep, chat_id: UUID, user_id:UUID
) -> Response:
    if not chat_id or not isinstance(chat_id, UUID):
        raise TypeError("chat_id should be uuid")

    if not user_id or not isinstance(user_id, UUID):
        raise TypeError("user_id should be UUID")

    try:
        logger.debug("Started to remove the chat")
        statement = (
            select(Chats).where(Chats.id == chat_id).where(Chats.user_id == user_id)
        )
        chat = session.exec(statement=statement).first()
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chat found for this user id",
            )

        session.delete(chat)
        session.commit()

        logger.debug("Successfully deleted the chat")
        return Response(status="success", message="Successfully removed the chat")

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to remove the chat for the user with user id: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while deleting the chat: {user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def update_chat(
    chat_id: UUID,
    details: UpdateChat,
    session: SessionDep,
    user_id: UUID,
) -> UUID:
    if not chat_id or not isinstance(chat_id, UUID):
        raise TypeError("chat_id should be uuid")

    if not user_id or not isinstance(user_id, UUID):
        raise TypeError("user_id should be uuid")

    try:
        logger.debug(f"Started with the updates of chat with id:{chat_id}")
        old_chat = session.get(Chats, chat_id)
        if not old_chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chat found for this chat id",
            )

        update_chat = details.model_dump(exclude_unset=True)

        for field, value in update_chat.items():
            setattr(old_chat, field, value)

        session.add(old_chat)
        session.commit()

        logger.debug(
            f"Successfully updated the chat for the chat with the id: {chat_id}, with the fields: {list(update_chat.keys())}"
        )

        return old_chat.id

    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to update the chat with the id:{chat_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Failed to update the chat with the id:{chat_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
