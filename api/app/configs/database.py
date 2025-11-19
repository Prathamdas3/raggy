from sqlmodel import create_engine, SQLModel, Session
from app.config import config
from fastapi import Depends
from app.utils.logger import get_logger
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

logger = get_logger(__name__)
URL = config.DATABASE_URI

def get_engine():
    try:
        engine = create_engine(
            URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,  # Add pool size
            max_overflow=20,  # Add overflow
        )
        logger.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logger.error(f"Error creating database engine: {e}")
        raise

# Global engine instance
engine = get_engine()

def init_db():
    """Run this once on startup — creates tables if not exist."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_session():
    """Yields a database session safely for FastAPI dependency injection."""
    session = Session(engine)
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_session)]

# ===== CELERY-SPECIFIC SESSION MANAGEMENT =====

@contextmanager
def get_celery_session():
    """
    Context manager for Celery tasks.
    Ensures proper session handling with commit/rollback.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()  # Auto-commit on success
    except Exception as e:
        session.rollback()
        logger.error(f"Celery session error: {e}", exc_info=True)
        raise
    finally:
        session.close()

def get_celery_session_no_autocommit():
    """
    Simple session factory for Celery tasks when you want manual commit control.
    Remember to call session.commit() and session.close() yourself!
    """
    return Session(engine)