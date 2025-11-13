from app.models.all_schema import Messages
from sqlmodel import Session, select
from app.utils.logger import get_logger
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.schemas.db.message import CreateMessage, UpdateMessage, GetAnswer
from uuid import UUID

logger = get_logger(__name__)


def create_message(session: Session, details: CreateMessage):
    try:
        logger.debug("Creating messages for with question and answer")

        if "question_id" in details:
            new_message = Messages(
                user_id=details.user_id,
                chat_id=details.chat_id,
                content=details.content,
                question_id=details.question_id,
                sender="llm",
            )
        else:
            new_message = Messages(
                user_id=details.user_id,
                chat_id=details.chat_id,
                content=details.content,
                sender="user",
            )

        session.add(new_message)
        session.commit()
        session.refresh(new_message)

        logger.debug("Successfully stored the message")
        return new_message.id

    except (SQLAlchemyError, IntegrityError):
        session.rollback()
        logger.error(
            f"Failed to create the message for the user with user_id:{details.user_id}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while creating the mesage with the chat: {details.chat_id}, user: {details.user_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operaion failed ",
        )


def update_message(session: Session, details: UpdateMessage) -> UUID:
    try:
        logger.debug("Starting to update message with audio link")
        statement = (
            select(Messages)
            .where(Messages.user_id == details.user_id)
            .where(Messages.chat_id == details.chat_id)
            .where(Messages.question_id == details.question_id)
        )
        message = session.exec(statement=statement).first()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="check chat_id, user_id or question_id",
            )

        for field, value in details.model_dump().items():
            setattr(message, field, value)

        session.add(message)
        session.commit()

        logger.debug("Successfully updated the message with the audio")

        return message.id

    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to update the message with the audio the id:{details.chat_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Failed to update the message with the audio the id:{details.chat_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def get_answer(session: Session, details: GetAnswer) -> Messages:
    try:
        logger.debug(
            f"Started to fetch the answer with the question_id: {details.question_id}"
        )
        statement = (
            select(Messages)
            .where(Messages.user_id == details.user_id)
            .where(Messages.chat_id == details.chat_id)
            .where(Messages.question_id == details.question_id)
        )
        message = session.exec(statement=statement).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="check chat_id, user_id or question_id",
            )
        return message
    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to fetch the message with the question id:{details.question_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(
            f"Failed to fetch the message with question id:{details.question_id}, error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
