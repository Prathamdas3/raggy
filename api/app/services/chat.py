"""Chat service for managing chat entities.

This module provides the ChatService class that handles all chat-related
business logic including creation, retrieval, updating, deletion,
sharing, and branching of chat conversations.
"""

from sqlmodel import select
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from typing import TypedDict, cast

from app.db import Chats, DatabaseService, ChatBranches
from app.models import UpdateChat
from app.core import get_logger, config

logger = get_logger(__name__)


class ReturnChatType(TypedDict):
    """Type definition for chat list return values."""

    title: str
    is_bookmarked: bool
    created_at: str


class ChatService:
    """Service class for managing chat operations.

    Handles all chat-related business logic including CRUD operations,
    sharing, and branching of conversations.
    """

    def __init__(self, db_session: DatabaseService):
        """Initialize ChatService with database session.

        Args:
            db_session: Database service instance.
        """
        self._db: DatabaseService = db_session

    def find_chat(self, chat_id: UUID) -> Chats:
        """Find a chat by its ID.

        Args:
            chat_id: UUID of the chat to find.

        Returns:
            The Chat entity.

        Raises:
            HTTPException: If chat is not found.
        """
        try:
            chat = self._db.session.get(Chats, chat_id)
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No chat found with the given id",
                )
            return chat
        except HTTPException:
            raise
        except Exception:
            logger.error(f"No chat found with the given id: {chat_id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong while fetching the chat",
            )

    def get_chats(self, user_id: UUID) -> list[ReturnChatType]:
        """Get all chats for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of chat metadata (title, bookmark status, created_at).
        """
        try:
            statement = select(
                {
                    "title": Chats.title,
                    "is_bookmarked": Chats.is_bookmarked,
                    "created_at": Chats.created_at,
                }
            ).where(Chats.user_id == user_id)
            chats = self._db.session.exec(statement=statement).fetchall()
            if not chats:
                return []
            return cast(list[ReturnChatType], chats)
        except Exception as e:
            logger.error(f"Failed to fetch the chats: {str(e)}", exc_info=True)
            raise HTTPException(
                detail="Failed to find the chats",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create_chat(self, user_id: UUID,title:str,original_doc:str) -> UUID:
        """Create a new chat for a user.

        Creates a new chat with a root branch for the conversation.

        Args:
            user_id: UUID of the user creating the chat.

        Returns:
            UUID of the newly created chat.

        Raises:
            HTTPException: If chat creation fails.
        """
        try:
            # 1. Create chat
            chat = Chats(user_id=user_id,title=title,original_doc=original_doc)
            self._db.session.add(chat)
            self._db.session.flush()  # get chat.id

            # 2. Create root branch
            chat_branch = ChatBranches(chat_id=chat.id)
            self._db.session.add(chat_branch)
            self._db.session.flush()  # get branch.id

            # 3. Set active branch
            chat.active_branch_id = chat_branch.id

            # 4. Commit once
            self._db.session.commit()

            return chat.id
        except Exception as e:
            logger.error("Failed to create a new chat", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store the chat",
            ) from e

    def remove_chat(self, chat_id: UUID) -> str:
        """Delete a chat by its ID.

        Args:
            chat_id: UUID of the chat to delete.

        Returns:
            Success message.

        Raises:
            HTTPException: If chat deletion fails.
        """
        try:
            chat = self.find_chat(chat_id=chat_id)
            self._db.session.delete(chat)
            self._db.commit()
            logger.info(f"Successfully removed the chat with the id: {chat_id}")
            return "Successfully removed the chat"
        except Exception:
            logger.error("Failed to remove the chat", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove the chat",
            )

    def update_chat(self, details: UpdateChat) -> str:
        """Update a chat's metadata.

        Args:
            chat_id: UUID of the chat to update.
            details: UpdateChat model with fields to update.

        Returns:
            Success message.

        Raises:
            HTTPException: If chat update fails.
        """
        try:
            chat = self.find_chat(chat_id=details.chat_id)
            updated_data = details.model_dump(exclude_unset=True)
            if not details.has_update():
                return "No data to update the chats"
            for key, value in updated_data.items():
                setattr(chat, key, value)
            self._db.session.add(chat)
            self._db.commit()
            self._db.session.refresh(chat)
            return "Successfully updated the chats"
        except Exception:
            logger.error("Failed to update the chat")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update the chat",
            )

    def share_chat(self, chat_id: UUID) -> str:
        """Generate or retrieve a shareable link for a chat.

        Args:
            chat_id: UUID of the chat to share.

        Returns:
            Shareable URL for the chat.

        Raises:
            HTTPException: If share ID generation fails.
        """
        try:
            chat = self.find_chat(chat_id=chat_id)
            if chat.share_id:
                return f"{config.frontend_url}/{chat.share_id}"

            code = str(uuid4())
            data = UpdateChat(share_id=code,chat_id=chat_id)
            self.update_chat(details=data)
            return f"{config.frontend_url}/{code}"
        except Exception:
            logger.error("Failed to generate a share_id")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create a share id",
            )

    def create_chat_branch(
        self, chat_id: UUID, parent_branch_id: UUID | None = None
    ) -> UUID:
        """Create a new branch in a chat for conversation branching.

        Args:
            chat_id: UUID of the parent chat.
            parent_branch_id: UUID of the parent branch (optional).

        Returns:
            UUID of the newly created branch.

        Raises:
            HTTPException: If branch creation fails.
        """
        try:
            data = ChatBranches(chat_id=chat_id, parent_branch_id=parent_branch_id)
            self._db.session.add(data)
            self._db.commit()
            self._db.session.refresh(data)
            return data.id
        except Exception as e:
            logger.error(f"Failed to create the branch: {str(e)}", exc_info=True)
            raise HTTPException(
                detail="Failed to create the branch",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
