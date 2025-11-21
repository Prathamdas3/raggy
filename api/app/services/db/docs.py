from sqlmodel import Session, select
from app.utils.logger import get_logger
from app.models.all_schema import Docs, Messages, Sender
from app.schemas.db import docs
from uuid import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.db.docs import UpdateDocsData

logger = get_logger(__name__)


def save_original_text(session: Session, data: docs.CreateText) -> UUID:
    try:
        logger.debug("Started to store new docs with the create original text")
        new_doc = Docs(
            user_id=data.user_id,
            chat_id=data.chat_id,
            original_text=data.original_text,
            summary_text="",
            audio_url="",
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
        raise
    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while creating the chat: {data.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise


def update_docs(session: Session, details: UpdateDocsData) -> UUID:
    try:
        logger.debug(
            f"Starting update for chat_id={details.chat_id}, question_id={details.question_id}"
        )

        # If no question_id, update Docs table
        if details.question_id is None:
            logger.debug("Updating Docs table (no question_id)")

            statement = (
                select(Docs)
                .where(Docs.chat_id == details.chat_id)
                .where(Docs.user_id == details.user_id)
            )
            doc = session.exec(statement).first()

            if doc is None:
                logger.error(
                    f"No doc found for chat_id={details.chat_id}, user_id={details.user_id}"
                )
                raise ValueError(f"No doc found for chat_id={details.chat_id}")

            # Only update the fields that are provided
            if details.summary_text is not None:
                doc.summary_text = details.summary_text
                logger.debug(
                    f"Updated summary_text (length: {len(details.summary_text)})"
                )

            if details.audio_url is not None:
                doc.audio_url = details.audio_url
                logger.debug(f"Updated audio_url: {details.audio_url}")

            session.add(doc)
            session.flush()  # Flush but don't commit

            logger.info(f"✅ Updated doc {doc.id} for chat_id={details.chat_id}")
            return doc.id

        # If question_id provided, update Messages table
        else:
            logger.debug(
                f"Creating new LLM message (answer to question_id={details.question_id})"
            )

            # First verify the question exists
            question = session.exec(
                select(Messages).where(Messages.id == details.question_id)
            ).first()

            if question is None:
                logger.error(f"Question message {details.question_id} not found")
                raise ValueError(f"Question message {details.question_id} not found")

            # Create new message for LLM's answer
            llm_message = Messages(
                chat_id=details.chat_id,
                user_id=details.user_id,
                question_id=details.question_id,  # References the user's question
                sender=Sender.llm,  # This is the LLM's response
                content=details.summary_text or "",
                audio_url=details.audio_url or "",
            )

            session.add(llm_message)
            session.flush()

            logger.info(
                f"✅ Created LLM message {llm_message.id} in response to question {details.question_id}"
            )
            return llm_message.id

    except ValueError as e:
        # Don't catch and re-raise as generic error
        logger.error(f"ValueError in update_docs: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_docs: {e}", exc_info=True)
        raise
