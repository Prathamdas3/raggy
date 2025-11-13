from sqlmodel import Session, select
from app.utils.logger import get_logger
from app.models.all_schema import Docs, Messages
from app.schemas.db import docs
from uuid import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from app.schemas.db.docs import UpdateDocsData

logger = get_logger(__name__)


def save_original_text(session: Session, data: docs.CreateText) -> UUID:
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


def update_docs(details: UpdateDocsData, session: Session) -> UUID:
    try:
        logger.debug(
            f"starting to update the summary text for chat_id:{details.chat_id}"
        )
        if details.question_id in details:
            statement = (
                select(Docs)
                .where(Docs.chat_id == details.chat_id)
                .where(Docs.user_id == details.user_id)
            )
            doc_data = session.exec(statement=statement).first()

            if doc_data is None:
                logger.error(f"No doc found with this chat_id:   {details.chat_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid chat id for fetching the summary",
                )

            for field, value in details.model_dump().items():
                setattr(doc_data, field, value)

            session.add(doc_data)
            session.commit()
        else:
            statement = (
                select(Messages)
                .where(Messages.chat_id == details.chat_id)
                .where(Messages.user_id == details.user_id)
                .where(Messages.question_id == details.question_id)
            )
            doc_data = session.exec(statement=statement).first()
            if doc_data is None:
                logger.error(f"No doc found with this chat_id:   {details.chat_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid chat id for fetching the summary",
                )

            for field, value in details.model_dump().items():
                setattr(doc_data, field, value)

            session.add(doc_data)
            session.commit()

        logger.debug(f"successfully updated the docs with chat_id of {details.chat_id}")
        return doc_data.id

    except Exception as e:
        logger.error(
            f"Unexpected error while fetching the summary of the chat: {details.chat_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
