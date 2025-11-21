import secrets
from app.models.all_schema import Chats, Docs, Messages
from fastapi import HTTPException, status
from app.utils.logger import get_logger
from sqlmodel import Session as SessionDep, select
from uuid import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.response import Response
from app.schemas.db.chat import GetSummary, UpdateChat

# from sqlalchemy.orm import aliased
from typing import Dict
# from app.schemas.db.message import MessageResponse

logger = get_logger(__name__)


def create_chat(session: SessionDep, user_id: UUID) -> UUID:
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


def get_chats(session: SessionDep, user_id: UUID) -> list[Chats]:
    if not user_id or not isinstance(user_id, UUID):
        raise TypeError("user_id must be an uuid type")

    try:
        logger.debug(f"Started fetching all the chats for the user with id:{user_id}")
        statement = select(Chats).where(Chats.user_id == user_id)
        chats = session.exec(statement=statement).all()

        if chats is None:
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


def remove_chat(session: SessionDep, chat_id: UUID, user_id: UUID) -> Response:
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


def update_chat(details: UpdateChat, session: SessionDep, chat_id: UUID) -> UUID:
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


def get_summary(details: GetSummary, session: SessionDep) -> Dict[str, str]:
    try:
        logger.debug(f"Starting to fetch the summary for cht_id:{details.chat_id}")
        statement = (
            select(Docs)
            .where(Docs.chat_id == details.chat_id)
            .where(Docs.user_id == details.user_id)
        )
        doc_data = session.exec(statement=statement).first()

        if doc_data is None:
            logger.error(f"No doc found with this chat_id: {details.chat_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chat id for fetching the summary",
            )

        logger.debug("Successfully fetched the docs for the summary")
        return {"summary_text": doc_data.summary_text, "audio_url": doc_data.audio_url}
    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to fetch the summary for the chat for the user with user id: {details.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while fetching the summary of the chat: {details.chat_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def get_chat_messages(details: GetSummary, session: SessionDep):
    try:
        logger.debug(
            "Getting strated to fetch the messages of user_id:{user_id} and cha_id:{chat_id}"
        )

        # Question = aliased(Messages)
        # Answer = aliased(Messages)

        # statement = (
        #     select(Question, Answer)
        #     .outerjoin(
        #         Answer, (Answer.question_id == Question.id) & (Answer.sender == "llm")
        #     )
        #     .where(Question.chat_id == details.chat_id)
        #      .where(Question.user_id==details.user_id)
        #     .where(Question.sender == "user")
        #     .order_by(Question.created_at.asc())
        # )
        statement = (
            select(Messages)
            .where(Messages.chat_id == details.chat_id)
            .where(Messages.user_id == details.user_id)
            .order_by(Messages.created_at.asc())
        )
        messages = session.exec(statement=statement).all()

        # messages_pair = []
        # for question, response in messages:
        #     messages_pair.append(
        #         {
        #             "question": MessageResponse.model_validate(question),
        #             "response": MessageResponse.model_validate(response)
        #             if response
        #             else None,
        #         }
        #     )

        logger.info(
            f"Successfully got all the messages under the chat_id {details.chat_id}"
        )

        return messages

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Integrity constraint violation while getting all the messages in the chat with id: {details.chat_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Violates database constraints"
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while getting all the messages in the chat with id {details.chat_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_original_text(details: GetSummary, session: SessionDep):
    try:
        logger.debug(
            f"Starting to fetch the original and summary also the tile of the chat with cht_id:{details.chat_id}"
        )
        statement = (
            select(Docs)
            .where(Docs.chat_id == details.chat_id)
            .where(Docs.user_id == details.user_id)
        )
        doc_data = session.exec(statement=statement).first()

        if doc_data is None:
            logger.error(f"No doc found with this chat_id: {details.chat_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chat id for fetching the summary",
            )

        logger.debug("Successfully fetched the docs for the summary")
        return {
            "summary_text": doc_data.summary_text,
            "original_text": doc_data.original_text,
            "title": doc_data.chat.chat_name,
        }
    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to fetch the summary for the chat for the user with user id: {details.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while fetching the summary of the chat: {details.chat_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def create_share_id(details: GetSummary, session: SessionDep) -> dict:
    try:
        logger.debug(f"Creating share id for chat: {details.chat_id}")

        chat = session.exec(
            select(Chats)
            .where(Chats.id == details.chat_id)
            .where(Chats.user_id == details.user_id)
        ).first()

        if not chat:
            raise HTTPException(
                status_code=400, detail="Chat not found or you do not own it"
            )

        # If already shared, return existing share_id
        if chat.share_id:
            return {"share_id": chat.share_id}

        # Generate opaque secure token
        new_share_id = secrets.token_urlsafe(16)

        chat.share_id = new_share_id
        session.add(chat)
        session.commit()
        session.refresh(chat)

        logger.debug(f"Successfully set share_id = {new_share_id} for chat {chat.id}")

        return {"share_id": chat.share_id}

    except Exception as e:
        session.rollback()
        logger.error(f"Error while creating share ID: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def get_chat_share_id(share_id: UUID, new_user_id: UUID, session: SessionDep) -> UUID:
    if not share_id:
        raise HTTPException(status_code=400, detail="Missing share_id")

    try:
        # 1. Fetch original chat
        old_chat = session.exec(select(Chats).where(Chats.share_id == share_id)).first()

        if not old_chat:
            raise HTTPException(status_code=404, detail="Shared chat not found")

        # 2. Create new chat
        new_chat = Chats(
            user_id=new_user_id,
            chat_name=old_chat.chat_name,
            is_bookmarked=False,
            share_id=None,  # forked chats are not shareable
        )

        session.add(new_chat)
        session.flush()  # new_chat.id is available now

        # 3. Clone Docs if exists
        old_docs = session.exec(select(Docs).where(Docs.chat_id == old_chat.id)).first()

        if old_docs:
            new_docs = Docs(
                user_id=new_user_id,
                chat_id=new_chat.id,
                summary_text=old_docs.summary_text,
                audio_url=old_docs.audio_url,
                original_text=old_docs.original_text,
            )
            session.add(new_docs)

        session.flush()

        # 4. Fetch all messages from old chat
        old_messages = session.exec(
            select(Messages)
            .where(Messages.chat_id == old_chat.id)
            .order_by(Messages.created_at.asc())
        ).all()

        # Mapping: old_message_id -> new_message_id
        id_map = {}

        # 5. First pass — create all messages (without question_id)
        for msg in old_messages:
            new_msg = Messages(
                chat_id=new_chat.id,
                user_id=new_user_id,
                sender=msg.sender,
                content=msg.content,
                audio_url=msg.audio_url,
                question_id=msg.question_id,
            )
            session.add(new_msg)
            session.flush()

            if new_msg.question_id is not None:
                id_map[msg.id] = new_msg.id

        # 6. Second pass — fix question_id mapping
        for msg in old_messages:
            if msg.sender == "llm" and msg.question_id:
                old_answer_id = id_map[msg.id]
                new_answer = session.get(Messages, old_answer_id)

                if msg.question_id in id_map:
                    new_answer.question_id = id_map[msg.question_id]

        # 7. Commit everything
        session.commit()

        return new_chat.id

    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"failed to clone the chat with share id {share_id}, error:{str(e)}",
            exc_info=True,
        )
        session.rollback()
        raise HTTPException(
            status_code=500, detail="Database operation failed (SQL issue)"
        )

    except Exception as e:
        logger.error(
            f"failed to clone the chat with share id {share_id}, error:{str(e)}",
            exc_info=True,
        )
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to fork chat")
