from pydantic import EmailStr
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

from app.core import get_logger
from app.db import Users, DatabaseService
from app.models import CreateUser, UpdateUser, Response, Status
from app.utils import HandlePassword

logger = get_logger(__name__)


@dataclass
class CreateNewUser:
    email: EmailStr
    id: str


class FindUser:
    def __init__(self, db_service: DatabaseService) -> None:
        self._db = db_service

    def get_user_by_id(self, user_id: UUID) -> Optional[Users]:
        try:
            logger.debug(f"Fetching user by id={user_id}")
            return self._db.session.get(Users, user_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch user by id={user_id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to find the user",
            ) from e

    def get_user_by_email(self, email: EmailStr) -> Optional[Users]:
        try:
            statement = select(Users).where(Users.email == email)
            return self._db.session.exec(statement).one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch user by email={email}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to find this user email",
            ) from e


class UserService:
    def __init__(
        self, db_session: DatabaseService, password: HandlePassword, find_user: FindUser
    ):
        self._db = db_session
        self._password = password
        self._user = find_user

    def get_current_user(self, user_id: str) -> Users | None:
        try:
            old_user = self._user.get_user_by_id(user_id=UUID(user_id))
            if not old_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User does not exists",
                )
            return old_user
        except HTTPException:
            raise
        except Exception as e:
            logger.error("User fetching failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user",
            ) from e

    def create_user(self, data: CreateUser) -> CreateNewUser:
        try:
            if self._user.get_user_by_email(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

            hashed_password = self._password.get_hashed_password(data.password)

            user = Users(
                email=data.email,
                password=hashed_password,
            )

            self._db.session.add(user)
            self._db.commit()
            self._db.session.refresh(user)

            logger.info(f"User created with id={user.id}")

            return CreateNewUser(id=str(user.id), email=user.email)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("User creation failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            ) from e

    def update_user(self, user_id: UUID, data: UpdateUser) -> Response[None]:
        try:
            if not data.has_updates():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            user = self._user.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            updates = data.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(user, field, value)

            self._db.session.add(user)
            self._db.commit()
            self._db.session.refresh(user)

            logger.info(f"User updated id={user_id}, fields={list(updates.keys())}")

            return Response[None](
                status=Status.success,
                message="User updated successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User update failed for id={user_id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user",
            ) from e

    def delete_user(self, user_id: UUID) -> Response[None]:
        try:
            user = self._user.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            self._db.session.delete(user)
            self._db.commit()

            logger.info(f"User deleted id={user_id}")

            return Response[None](
                status=Status.success,
                message="User deleted successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User deletion failed for id={user_id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            ) from e
