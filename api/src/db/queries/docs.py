from db.index import SessionDep
from db.schema import Docs
from lib.logger import get_logger
from fastapi import HTTPException, status
from sqlmodel import select
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional
import uuid

logger = get_logger("db/queries/docs")


class UpdateDocs(BaseModel):
    summary_text: Optional[str] = None
    audio_url: Optional[str] = None

    class Config:
        exclude_unset = True


def create_docs(doc: Docs, session: SessionDep):
    try:
        logger.info("Creating new docs")

        session.add(doc)
        session.commit()
        session.refresh(doc)

        logger.info(f"Successfully created new docs with id:{doc.id}")
        return doc

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity constraint violation while creating docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat already exists or violates database constraints",
        )

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while creating docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while creating docs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def update_docs(chat_id: uuid.UUID, docs_update: UpdateDocs, session: SessionDep):
    try:
        logger.info("Starting the update process for the docs with chat_id:{chat_id}")
        statement = select(Docs).where(Docs.chat_id == chat_id)
        docs = session.exec(statement).first()

        if not docs:
            logger.error(f"No docs found with the given chat id:{chat_id}")
            raise HTTPException(
                status_code=404, detail="No docs found with the given id"
            )

        update_data = docs_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(docs, field, value)

        session.add(docs)
        session.commit()
        session.refresh(docs)

        logger.info(
            f"Successfully updated docs with the chat_id:{chat_id} with fields: {list(update_data)}"
        )

        return docs

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity constraint violation while updating docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat already exists or violates database constraints",
        )

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while updating docs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_docs_with_chat_id(chat_id: uuid.UUID, session: SessionDep):
    try:
        logger.info("Getting the summary for the docs")
        statement = select(Docs).where(Docs.chat_id == chat_id)
        docs = session.exec(statement=statement).first()

        if not statement:
            logger.error(f"No docs found for the given chat_id:{chat_id}")
            raise HTTPException(status_code=404, detail="No docs found")

        return docs

    except SQLAlchemyError as e:
        logger.error(
            f"Database error while getting the docs with chat_id:{chat_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Databases operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while getting doc: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
