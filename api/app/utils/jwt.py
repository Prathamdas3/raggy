from datetime import datetime, timezone, timedelta
from uuid import UUID
from jose import jwt, JWTError
from fastapi import Request, status, Depends
from pydantic import EmailStr
from dataclasses import dataclass
from app.core import config, AppException, get_logger,SessionDep
from app.models.jwt import Tokens
from app.schemas import Users
from typing import Annotated
from sqlmodel import Session

logger = get_logger(__name__)


@dataclass
class CurrentUser:
    user_id: UUID
    email: EmailStr



def create_access_token(payload: Tokens) -> str:
    try:
        data = payload.model_dump()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=config.access_token_expire_minutes or 15
        )
        data.update({"exp": expire, "type": "access", "iat": datetime.now()})
        return jwt.encode(data, config.secret_key, algorithm=config.algorithm)
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise AppException(status_code=500, message="Failed to form jwt")


def create_refresh_token(payload: Tokens) -> str:
    try:
        data = payload.model_dump()
        expire = datetime.now(timezone.utc) + timedelta(
            days=config.refresh_token_expire_days or 7
        )
        data.update({"exp": expire, "type": "refresh", "iat": datetime.now()})
        return jwt.encode(data, config.secret_key, algorithm=config.algorithm)
    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise AppException(status_code=500, message="Failed to form token")



def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, config.secret_key, algorithms=config.algorithm)
    except JWTError as e:
        logger.error(f"JWT decode failed: {e}")
        raise AppException(status_code=status.HTTP_401_UNAUTHORIZED, message="Could not validate credentials")


def _get_user_or_raise(session: Session, user_id: str) -> Users:
    try:
        uid = UUID(user_id)
    except Exception:
        raise AppException(status_code=401, message="Invalid user id in token")

    user = session.get(Users, uid)
    if not user:
        raise AppException(status_code=401, message="User not found")
    return user




def get_current_user(request: Request, session: SessionDep) -> CurrentUser:
    token = request.cookies.get("jwt")
    if not token:
        raise AppException(status_code=401, message="Not authenticated")

    payload = _decode_token(token)
    user_id: str | None = payload.get("user_id")
    email: str | None = payload.get("email")

    if not user_id or not email or payload.get("type") != "access":
        raise AppException(status_code=401, message="Invalid token")

    _get_user_or_raise(session, user_id)
    return CurrentUser(user_id=UUID(user_id), email=email)


def get_current_user_from_refresh(request: Request, session: SessionDep) -> CurrentUser:
    token = request.cookies.get("token")
    if not token:
        raise AppException(status_code=401, message="Not authenticated")

    payload = _decode_token(token)
    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email or payload.get("type") != "refresh":
        raise AppException(status_code=401, message="Invalid token")

    _get_user_or_raise(session, str(user_id))
    return CurrentUser(user_id=UUID(str(user_id)), email=email)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserRefreshDep = Annotated[CurrentUser, Depends(get_current_user_from_refresh)]