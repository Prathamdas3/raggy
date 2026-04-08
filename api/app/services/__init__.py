"""Service layer initialization.

Provides dependency injection functions for FastAPI endpoints.
"""

from app.db.async_db import SessionDep
from app.db import AsyncDatabaseService
from app.utils.common import HandlePassword
from app.services.auth import AuthService
from app.services.user import UserService, FindUser
from app.services.chat import ChatService, UpdateChat
from app.services.summary import SummaryService


def get_auth_service(session: SessionDep) -> AuthService:
    """Get authentication service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured AuthService instance.
    """
    password = HandlePassword()
    db_session = AsyncDatabaseService(db=session)
    user = FindUser(db=db_session)
    return AuthService(db=db_session, user=user, password=password)


def get_user_service(session: SessionDep) -> UserService:
    """Get user service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured UserService instance.
    """
    db_session = AsyncDatabaseService(db=session)
    user = FindUser(db=db_session)
    password = HandlePassword()
    return UserService(db=db_session, find_user=user, password=password)


def get_chat_service(session: SessionDep) -> ChatService:
    """Get chat service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured ChatService instance.
    """
    db_session = AsyncDatabaseService(db=session)
    return ChatService(db_session=db_session)

def get_summary_service(session:SessionDep)->SummaryService:
    db_session=AsyncDatabaseService(db=session)
    return SummaryService(db_service=db_session)

__all__ = ["UpdateChat"]
