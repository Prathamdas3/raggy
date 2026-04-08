"""Summary service for managing chat summaries.

This module provides the SummaryService class that handles
generation and retrieval of chat summaries in different variants.
"""

from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing import Mapping, cast
from app.core import AppException
from uuid import UUID
from fastapi import status
from app.db.schemas import SummaryVariants, VariantType
from app.db.async_service import AsyncDatabaseService
from app.core import get_logger
from app.models import UpdateSummary
from sqlmodel import select

logger = get_logger(__name__)


class SummaryService:
    """Service class for managing chat summaries.

    Handles creation, retrieval, and updating of chat summaries
    with different variant types (short, long, detailed).
    """

    def __init__(self, db_service: AsyncDatabaseService):
        """Initialize SummaryService with database session.

        Args:
            db_service: Database service instance.
        """
        self._db: AsyncDatabaseService = db_service

    async def get_summaries(self, chat_id: str) -> list[dict[str, str]]:
        """Get all summaries for a chat.

        Args:
            chat_id: UUID of the chat.

        Returns:
            List of summary dictionaries with content, audio_url, and created_at.

        Raises:
            AppException: If no summaries found or fetch fails.
        """
        try:
            chat_id:UUID=UUID(chat_id)
        except Exception:
            raise AppException(status_code=400,message="Chat id must be of valid id")
        
        try:
            statement: SelectOfScalar[Mapping[str, str]] = select(
                {
                    "content": SummaryVariants.content,
                    "audio_url": SummaryVariants.audio_url,
                    "create_at": SummaryVariants.created_at,
                }
            ).where(SummaryVariants.chat_id == chat_id)
            summaries =await self._db.session.execute(statement=statement)
            summaries=summaries.all()
            if not summaries:
                raise AppException(
                    message="No summaries found", status_code=status.HTTP_400_BAD_REQUEST
                )
            return cast(list[dict[str, str]], summaries)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to get the summaries from the chat_id: {str(e)}",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to fetch the summaries",
            )

    async def create_summary(self, chat_id: UUID, variant_type: VariantType=VariantType.detailed) -> UUID:
        """Create a new summary for a chat.

        Args:
            chat_id: UUID of the parent chat.
            summary: Summary content text.
            variant_type: Type of summary (short, long, detailed).

        Returns:
            UUID of the created summary.

        Raises:
            AppException: If summary creation fails.
        """
        try:
            data = SummaryVariants(chat_id=chat_id, variant_type=variant_type)
            self._db.add(data)
            await self._db.commit()
            await self._db.refresh(data)
            return data.id
        except Exception as e:
            logger.error(
                f"Failed to create a new summary: {str(e)}",
            )
            raise AppException(
                message="Failed to save the summary",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def update_summary(self, data: UpdateSummary) -> str:
        try:
            if not data.has_update():
                raise AppException(message="No data found to update", status_code=status.HTTP_400_BAD_REQUEST)

            summary = await self._db.session.get(SummaryVariants, data.summary_id)
            if not summary:
                raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Summary not found.",
                )

            # only update fields that were actually provided
            if data.content is not None:
                summary.content = data.content
            if data.audio_url is not None:
                summary.audio_url = data.audio_url

            self._db.add(summary)
            await self._db.commit()
            await self._db.refresh(summary)
            return summary.audio_url

        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to update summary: {e}",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to update summary.",
            )
