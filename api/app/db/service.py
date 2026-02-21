from sqlmodel import Session
from fastapi import status, HTTPException
from app.core.logger import get_logger
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = get_logger(__name__)


class DatabaseService:
    def __init__(self, session: Session):
        self._db = session

    def commit(self) -> None:
        try:
            self._db.commit()
        except (IntegrityError, SQLAlchemyError) as e:
            self._db.rollback()
            logger.error("Database operation failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed",
            ) from e

    @property
    def session(self) -> Session:
        return self._db

    def refresh(self, instance) -> None:
        self._db.refresh(instance)
