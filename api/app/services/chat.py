"""Chat service for managing chat entities.

This module provides the ChatService class that handles all chat-related
business logic including creation, retrieval, updating, deletion,
sharing, and branching of chat conversations.
"""


from sqlmodel import select
from fastapi import status
from uuid import UUID, uuid4
from typing import TypedDict, cast
from app.core.exceptions import AppException

from app.db.schemas import Chats, ChatBranches
from app.db import AsyncDatabaseService
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

    def __init__(self, db_session: AsyncDatabaseService):
        """Initialize ChatService with database session.

        Args:
            db_session: Database service instance.
        """
        self._db: AsyncDatabaseService = db_session

    async def find_chat(self, chat_id: UUID) -> Chats:
        """Find a chat by its ID.

        Args:
            chat_id: UUID of the chat to find.

        Returns:
            The Chat entity.

        Raises:
            AppException: If chat is not found.
        """
        try:
            chat = await self._db.session.get(Chats, chat_id)
            if not chat:
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="No chat found with the given id",
                )
            return chat
        except AppException:
            raise
        except Exception:
            logger.error(
                f"No chat found with the given id: {chat_id}",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong while fetching the chat",
            )

    async def get_chats(self, user_id: UUID) -> list[ReturnChatType]:
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
            chats = await self._db.session.execute(statement=statement)
            chats = chats.fetchall()
            if not chats:
                return []
            return cast(list[ReturnChatType], chats)
        except Exception as e:
            logger.error(
                f"Failed to fetch the chats: {str(e)}",
            )
            raise AppException(
                message="Failed to find the chats",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def create_chat(self, user_id: UUID, title: str, original_doc: str) -> UUID:
        """Create a new chat for a user.

        Creates a new chat with a root branch for the conversation.

        Args:
            user_id: UUID of the user creating the chat.

        Returns:
            UUID of the newly created chat.

        Raises:
            AppException: If chat creation fails.
        """
        try:
            # 1. Create chat
            chat = Chats(user_id=user_id, title=title, original_doc=original_doc)
            self._db.add(chat)
            await self._db.session.flush()  # get chat.id

            # 2. Create root branch
            chat_branch = ChatBranches(chat_id=chat.id)
            self._db.add(chat_branch)
            await self._db.session.flush()  # get branch.id

            # 3. Set active branch
            chat.active_branch_id = chat_branch.id

            # 4. Commit once
            await self._db.commit()

            return chat.id
        except Exception as e:
            logger.error(
                "Failed to create a new chat",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to store the chat",
            ) from e

    async def remove_chat(self, chat_id: UUID) -> str:
        """Delete a chat by its ID.

        Args:
            chat_id: UUID of the chat to delete.

        Returns:
            Success message.

        Raises:
            AppException: If chat deletion fails.
        """
        try:
            chat = self.find_chat(chat_id=chat_id)
            await self._db.session.delete(chat)
            await self._db.commit()
            logger.info(f"Successfully removed the chat with the id: {chat_id}")
            return "Successfully removed the chat"
        except Exception:
            logger.error(
                "Failed to remove the chat",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to remove the chat",
            )

    async def update_chat(self, details: UpdateChat) -> str:
        """Update a chat's metadata.

        Args:
            chat_id: UUID of the chat to update.
            details: UpdateChat model with fields to update.

        Returns:
            Success message.

        Raises:
            AppException: If chat update fails.
        """
        try:
            chat_id = details.chat_id
            if not isinstance(chat_id, UUID):
                chat_id = UUID(chat_id)
            chat = self.find_chat(chat_id=chat_id)
            updated_data = details.model_dump(exclude_unset=True, exclude={"chat_id"})
            if not details.has_update():
                raise AppException(status_code=status.HTTP_400_BAD_REQUEST,message="No content to update")
            for key, value in updated_data.items():
                setattr(chat, key, value)
            self._db.add(chat)
            await self._db.commit()
            await self._db.refresh(chat)
            return "Successfully updated the chats"
        except AppException as e:
            logger.exception(f"Failed to update chat: {e}")
            raise

    async def share_chat(self, chat_id: UUID) -> str:
        """Generate or retrieve a shareable link for a chat.

        Args:
            chat_id: UUID of the chat to share.

        Returns:
            Shareable URL for the chat.

        Raises:
            AppException: If share ID generation fails.
        """
        try:
            chat = await self.find_chat(chat_id=chat_id)
            if chat.share_id:
                return f"{config.frontend_url}/{chat.share_id}"

            code = str(uuid4())
            data = UpdateChat(share_id=code, chat_id=str(chat_id))
            await self.update_chat(details=data)
            return f"{config.frontend_url}/{code}"
        except Exception:
            logger.error("Failed to generate a share_id")
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to create a share id",
            )

    async def create_chat_branch(
        self, chat_id: UUID, parent_branch_id: UUID | None = None
    ) -> UUID:
        """Create a new branch in a chat for conversation branching.

        Args:
            chat_id: UUID of the parent chat.
            parent_branch_id: UUID of the parent branch (optional).

        Returns:
            UUID of the newly created branch.

        Raises:
            AppException: If branch creation fails.
        """
        try:
            data = ChatBranches(chat_id=chat_id, parent_branch_id=parent_branch_id)
            self._db.add(data)
            await self._db.commit()
            await self._db.session.refresh(data)
            return data.id
        except Exception as e:
            logger.error(
                f"Failed to create the branch: {str(e)}",
            )
            raise AppException(
                message="Failed to create the branch",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
