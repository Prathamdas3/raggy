"""Database service wrapper.

Provides DatabaseService class for encapsulating common database operations.
"""

from sqlmodel import Session
from fastapi import status, HTTPException
from app.core.logger import get_logger
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = get_logger(__name__)


class DatabaseService:
    """Service wrapper for SQLModel Session.

    Provides common database operations with error handling
    and automatic rollback on failure.
    """

    def __init__(self, session: Session):
        """Initialize DatabaseService with session.

        Args:
            session: SQLModel session instance.
        """
        self._db = session

    def commit(self) -> None:
        """Commit the current transaction.

        Raises:
            HTTPException: If commit fails due to integrity or SQL error.
        """
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
        """Get the underlying session.

        Returns:
            SQLModel session instance.
        """
        return self._db

    def refresh(self, instance) -> None:
        """Refresh an instance from the database.

        Args:
            instance: SQLModel instance to refresh.
        """
        self._db.refresh(instance)
