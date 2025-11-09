from sqlmodel import Session
from app.utils.logger import get_logger
from app.models.all_schema import Docs
from app.schemas.db import docs
from uuid import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

logger = get_logger(__name__)


def create_original_text(session: Session, data: docs.CreateText) -> UUID:
    try:
        logger.debug("Started to store new docs with the create original text")
        new_doc = Docs(
            user_id=data.user_id, chat_id=data.chat_id, original_text=data.original_text
        )
        session.add(new_doc)
        session.commit()
        session.refresh(new_doc)
        logger.debug(
            f"docs created successfully for the user_id: {data.user_id}, chat_id:{data.chat_id}, with the id:{new_doc.id}"
        )
        return new_doc.id
    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to create the chat for the user with user id: {data.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while creating the chat: {data.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
