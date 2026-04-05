from sqlalchemy.ext.asyncio import AsyncSession
from app.core import get_logger

logger = get_logger(__name__)


class AsyncDatabaseService:
    def __init__(self, db: AsyncSession):
        self._db = db

    @property
    def session(self) -> AsyncSession:
        return self._db

    def add(self, instance) -> None:  # ← sync, no async
        self._db.add(instance)

    async def commit(self) -> None:
        try:
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def refresh(self, instance) -> None:
        await self._db.refresh(instance)

    async def delete(self, instance) -> None:
        await self._db.delete(instance)