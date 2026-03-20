"""Summary service for managing chat summaries.

This module provides the SummaryService class that handles
generation and retrieval of chat summaries in different variants.
"""

from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing import Mapping, cast

from uuid import UUID
from fastapi import HTTPException, status
from app.db import SummaryVariants, DatabaseService, VariantType
from app.core import get_logger
from sqlmodel import select

logger = get_logger(__name__)


class SummaryService:
    """Service class for managing chat summaries.

    Handles creation, retrieval, and updating of chat summaries
    with different variant types (short, long, detailed).
    """

    def __init__(self, db_service: DatabaseService):
        """Initialize SummaryService with database session.

        Args:
            db_service: Database service instance.
        """
        self._db = db_service

    def get_summaries(self, chat_id: UUID) -> list[dict[str, str]]:
        """Get all summaries for a chat.

        Args:
            chat_id: UUID of the chat.

        Returns:
            List of summary dictionaries with content, audio_url, and created_at.

        Raises:
            HTTPException: If no summaries found or fetch fails.
        """
        try:
            statement: SelectOfScalar[Mapping[str, str]] = select(
                {
                    "content": SummaryVariants.content,
                    "audio_url": SummaryVariants.audio_url,
                    "create_at": SummaryVariants.created_at,
                }
            ).where(SummaryVariants.chat_id == chat_id)
            summaries = self._db.session.exec(statement=statement).all()
            if not summaries:
                raise HTTPException(
                    detail="No summaries found", status_code=status.HTTP_400_BAD_REQUEST
                )
            return cast(list[dict[str, str]], summaries)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to get the summaries from the chat_id: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch the summaries",
            )

    def create_summary(
        self, chat_id: UUID, summary: str, variant_type: VariantType
    ) -> UUID:
        """Create a new summary for a chat.

        Args:
            chat_id: UUID of the parent chat.
            summary: Summary content text.
            variant_type: Type of summary (short, long, detailed).

        Returns:
            UUID of the created summary.

        Raises:
            HTTPException: If summary creation fails.
        """
        try:
            data = SummaryVariants(
                content=summary, chat_id=chat_id, variant_type=variant_type
            )
            self._db.session.add(data)
            self._db.commit()
            self._db.session.refresh(data)
            return data.id
        except Exception as e:
            logger.error(f"Failed to create a new summary: {str(e)}", exc_info=True)
            raise HTTPException(
                detail="Failed to save the summary",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update_summary_audio(self, summary_id: UUID, audio_path: str) -> str:
        """Update a summary with an audio URL.

        Args:
            summary_id: UUID of the summary to update.
            audio_path: URL or path to the audio file.

        Returns:
            Updated audio_url.

        Raises:
            HTTPException: If summary not found or update fails.
        """
        try:
            data = self._db.session.get(SummaryVariants, summary_id)
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Chat not found"
                )

            setattr(data, "audio_url", audio_path)
            self._db.session.add(data)
            self._db.commit()
            self._db.session.refresh(data)
            return data.audio_url
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to store the audio url:{str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update the summary with audio url",
            )
