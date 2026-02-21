from app.db.db import SessionDep
from app.services.auth import AuthService
from app.services.user import UserService, FindUser
from app.db import DatabaseService
from app.utils.common import HandlePassword


def get_auth_service(session: SessionDep):
    password = HandlePassword()
    db_session = DatabaseService(session=session)
    user = FindUser(db_service=db_session)
    return AuthService(db_service=db_session, user=user, password=password)


def get_user_service(session: SessionDep):
    db_session = DatabaseService(session=session)
    user = FindUser(db_service=db_session)
    password = HandlePassword()
    return UserService(db_session=db_session, find_user=user, password=password)
