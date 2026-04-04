"""Database connection and session management.

Provides Database class for engine creation and session factory,
and dependency injection functions for FastAPI.
"""

from contextlib import contextmanager
from sqlmodel import create_engine, Session
from fastapi import Depends
from app.core.logger import get_logger
from app.core.config import config
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, Annotated

logger = get_logger(__name__)
URL = config.database_url


class Database:
    """Database connection manager.

    Manages SQLAlchemy engine creation, session generation,
    and database initialization.
    """

    def __init__(
        self,
        url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_recycle: int = 1800,
        echo: bool = False,
    ):
        """Initialize Database with connection parameters.

        Args:
            url: Database connection URL.
            pool_size: Connection pool size.
            max_overflow: Maximum pool overflow.
            pool_recycle: Pool recycle time in seconds.
            echo: Enable SQL echo mode.
        """
        self.url = url
        self.engine = self._create_engine(pool_size, max_overflow, pool_recycle, echo)

    def _create_engine(
        self, pool_size: int, max_overflow: int, pool_recycle: int, echo: bool
    ):
        """Create SQLAlchemy engine with pooling configuration."""
        try:
            engine = create_engine(
                self.url,
                echo=echo,
                pool_pre_ping=True,
                pool_recycle=pool_recycle,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )
            return engine
        except Exception:
            raise

    def session(self) -> Generator[Session, None, None]:
        """Generate database session for request lifecycle.

        Yields:
            Session instance.

        Handles rollback on error and cleanup on exit.
        """
        db = Session(self.engine)
        try:
            yield db
        except SQLAlchemyError:
            db.rollback()
            raise

        finally:
            db.close()


db = Database(url=URL)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session.

    Yields:
        Database session for the request.
    """
    yield from db.session()


SessionDep = Annotated[Session, Depends(get_session)]


@contextmanager
def get_celery_session():
    """Context manager for Celery task database sessions.

    Yields:
        Database session for background tasks.

    Handles rollback on error and cleanup on exit.
    """
    session = Session(db.engine)
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(
            f"Celery session error: {e}",
        )
        raise
    finally:
        session.close()
