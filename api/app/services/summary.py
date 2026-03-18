from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing import Mapping, cast

from uuid import UUID
from fastapi import HTTPException, status
from app.db import SummaryVariants, DatabaseService, VariantType
from app.core import get_logger
from sqlmodel import select

logger = get_logger(__name__)


class SummaryService:
    def __init__(self, db_service: DatabaseService):
        self._db = db_service

    def get_summaries(self, chat_id: UUID) -> list[dict[str, str]]:
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
                f"Failed ot get the summaries from the chat_id: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch the summaries",
            )

    def create_summary(self, chat_id: UUID, summary: str, type: VariantType) -> UUID:
        try:
            data = SummaryVariants(content=summary, chat_id=chat_id, variant_type=type)
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
