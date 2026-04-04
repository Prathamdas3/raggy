from app.core import get_logger

logger=get_logger(__name__)

class AsyncDatabaseService:
    def __init__(self,db):
        self._db = db
    
    async def commit(self):
        try:
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            raise e
    
    @property
    def session(self):
        return self._db
    async def refresh(self, instance):
        await self._db.refresh(instance)