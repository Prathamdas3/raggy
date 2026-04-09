from uuid import UUID
from app.core import AppException, get_logger
from app.models import UpdateSummary
from app.schemas import SummaryVariants, VariantType

logger = get_logger(__name__)


class SummaryService:
    def __init__(self, repo):
        self._repo = repo

    def _find_summary(self, summary_id: UUID) -> SummaryVariants:
        summary = self._repo.get_by_id(summary_id)
        if not summary:
            raise AppException(status_code=404, message="Summary not found")
        return summary

    def get_summaries(self, chat_id: str) -> list[dict]:
        try:
            uid = UUID(chat_id)
        except Exception:
            raise AppException(status_code=400, message="Chat id must be a valid UUID")
        summaries = self._repo.get_summaries(uid)
        if not summaries:
            raise AppException(status_code=404, message="No summaries found")
        return summaries

    def create_summary(self, chat_id: UUID, variant_type: VariantType = VariantType.detailed) -> UUID:
        return self._repo.create_summary(chat_id, variant_type)

    def update_summary(self, data: UpdateSummary) -> str:
        if not data.has_update():
            raise AppException(status_code=400, message="No data to update")
        summary = self._find_summary(data.summary_id)
        if data.content is not None:
            summary.content = data.content
        if data.audio_url is not None:
            summary.audio_url = data.audio_url
        saved = self._repo.save(summary)
        return saved.audio_url