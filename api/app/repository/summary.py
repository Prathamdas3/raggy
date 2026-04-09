from uuid import UUID
from sqlmodel import select
from sqlmodel import Session
from app.schemas import SummaryVariants, VariantType


class SummaryRepo:
    def __init__(self, session: Session):
        self._db = session

    def get_summaries(self, chat_id: UUID) -> list[dict]:
        rows = self._db.exec(
            select(SummaryVariants).where(SummaryVariants.chat_id == chat_id)
        ).all()
        return [{"content": r.content, "audio_url": r.audio_url, "created_at": r.created_at} for r in rows]

    def create_summary(self, chat_id: UUID, variant_type: VariantType) -> UUID:
        data = SummaryVariants(chat_id=chat_id, variant_type=variant_type)
        self._db.add(data)
        self._db.commit()
        self._db.refresh(data)
        return data.id

    def get_by_id(self, summary_id: UUID) -> SummaryVariants | None:
        return self._db.get(SummaryVariants, summary_id)

    def save(self, instance: SummaryVariants) -> SummaryVariants:
        self._db.add(instance)
        self._db.commit()
        self._db.refresh(instance)
        return instance

