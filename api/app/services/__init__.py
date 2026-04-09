"""Service layer initialization.

Provides dependency injection functions for FastAPI endpoints.
"""

from app.core import SessionDep
from app.utils.common import HandlePassword
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.chat import ChatService, UpdateChat
from app.services.summary import SummaryService
from app.repository import UserRepo, ChatRepo, SummaryRepo


def get_auth_service(session: SessionDep) -> AuthService:
    """Get authentication service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured AuthService instance.
    """
    password = HandlePassword()
    repo = UserRepo(session=session)
    return AuthService(password=password, repo=repo)


def get_user_service(session: SessionDep) -> UserService:
    """Get user service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured UserService instance.
    """
    repo = UserRepo(session)
    password = HandlePassword()
    return UserService(repo=repo, password=password)


def get_chat_service(session: SessionDep) -> ChatService:
    """Get chat service instance.

    Args:
        session: Database session dependency.

    Returns:
        Configured ChatService instance.
    """
    repo = ChatRepo(session=session)
    return ChatService(repo=repo)


def get_summary_service(session: SessionDep) -> SummaryService:
    repo = SummaryRepo(session=session)
    return SummaryService(repo=repo)


__all__ = [
    "UpdateChat",
    "get_summary_service",
    "get_chat_service",
    "get_user_service",
    "get_auth_service",
]
