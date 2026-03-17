from app.db.db import SessionDep
from app.db import DatabaseService
from app.utils.common import HandlePassword
from app.services.auth import AuthService
from app.services.user import UserService, FindUser
from app.services.docs import DocsService


def get_auth_service(session: SessionDep) -> AuthService:
    password = HandlePassword()
    db_session = DatabaseService(session=session)
    user = FindUser(db_service=db_session)
    return AuthService(db_service=db_session, user=user, password=password)


def get_user_service(session: SessionDep) -> UserService:
    db_session = DatabaseService(session=session)
    user = FindUser(db_service=db_session)
    password = HandlePassword()
    return UserService(db_session=db_session, find_user=user, password=password)


def get_docs_service(session: SessionDep) -> DocsService:
    db_session = DatabaseService(session=session)
    return DocsService(db_session=db_session)
