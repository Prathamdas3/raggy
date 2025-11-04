from typing import Optional
from db.index import SessionDep
from db.schema import Messages
from lib.logger import get_logger
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select
from pydantic import BaseModel, field_validator
import uuid

logger = get_logger("db/queries/messages")


class UpdateAudio(BaseModel):
    audio_url: Optional[str] = None

    class Config:
        exclude_unset = True

    @field_validator("audio_url")
    @classmethod
    def validate_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty or just whitespace")

        return v.strip() if v else v

    def has_update(self) -> bool:
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())


def create_message(message: Messages, session: SessionDep):
    try:
        logger.info("Creating new message")

        session.add(message)
        session.commit()
        session.refresh(message)

        logger.info("Successfully created the message")
        return message

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity constraint violation while creating chat:{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Message already exists or violates database constraints",
        )

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while creating message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while creating message: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_answer(question_id: uuid.UUID, session: SessionDep):
    try:
        logger.info("Getting the answer")
        statement = select(Messages).where(Messages.question_id == question_id)
        answer = session.exec(statement=statement).first()

        if not answer:
            logger.error(f"No answer found for the given question_id: {question_id}")
            raise HTTPException(status_code=404, detail="No answer found")

        return answer

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        logger.error(
            f"Database error while getting the answer with question_id: {question_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while getting answer with question_id: {question_id}, {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def update_audio_url(
    question_id: uuid.UUID, audio_url: UpdateAudio, session: SessionDep
):
    try:
        if not audio_url.has_update():
            logger.warning(f"Update attempt with no fields for chat Id: {question_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        logger.info(
            "Starting the udpate process for the answer with the quesion_id: {question_id}"
        )
        statement = select(Messages).where(Messages.question_id == question_id)
        answer = session.exec(statement=statement).first()

        if not answer:
            logger.error(f"No answer found with the given question id: {question_id}")
            raise HTTPException(
                status_code=404, detail="No answer found with the question id"
            )

        update_data = audio_url.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(answer, field, value)

        session.add(answer)
        session.commit()
        session.refresh(answer)

        logger.info(
            f"Successfully updated answer with the question_id: {question_id} with the field: {list(update_data)}"
        )

        return answer

    except HTTPException:
        raise

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity constraint violation while updating docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Violates database constraints"
        )

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Unexpected error while updating docs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while updating audio url: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
