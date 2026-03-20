"""Authentication service for user sign-up and sign-in.

This module provides the AuthService class that handles user registration,
login, and password update operations.
"""

from dataclasses import dataclass
from fastapi import HTTPException, status
from pydantic import EmailStr


from app.core import get_logger
from app.models import CreateUser, SigninUser, UpdatePassword, Response, Status
from app.services.user import FindUser
from app.db import DatabaseService
from app.utils import HandlePassword

logger = get_logger(__name__)


@dataclass
class SignInUser:
    """Data class for sign-in response."""

    id: str
    email: EmailStr


class AuthService:
    """Service class for authentication operations.

    Handles user signup, signin, and password update operations.
    """

    def __init__(
        self, db_service: DatabaseService, password: HandlePassword, user: FindUser
    ):
        """Initialize AuthService with dependencies.

        Args:
            db_service: Database service instance.
            password: Password handler for hashing/verification.
            user: FindUser service for user lookup.
        """
        self._db = db_service
        self._password = password
        self._user = user

    def user_signup(self, data: CreateUser):
        """Register a new user.

        Args:
            data: CreateUser model with email and password.

        Returns:
            Dictionary with created user's id and email.

        Raises:
            HTTPException: If email already exists or signup fails.
        """
        try:
            existing = self._user.get_user_by_email(data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

            hashed_password = self._password.get_hashed_password(data.password)

            from app.db.schema import Users

            new_user = Users(email=data.email, password=hashed_password)
            self._db.session.add(new_user)
            self._db.commit()
            self._db.session.refresh(new_user)

            logger.info(f"User created with id={new_user.id}")

            return {"id": str(new_user.id), "email": new_user.email}

        except HTTPException:
            raise
        except Exception as e:
            logger.error("User signup failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            ) from e

    def user_signin(self, data: SigninUser) -> SignInUser:
        """Authenticate a user with email and password.

        Args:
            data: SigninUser model with email and password.

        Returns:
            SignInUser with authenticated user's id and email.

        Raises:
            HTTPException: If user not found or password incorrect.
        """
        try:
            user = self._user.get_user_by_email(data.email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No user found with the given email",
                )

            old_password = user.password
            new_password = data.password

            if not self._password.verify_password(
                plain_password=new_password, hashed_password=old_password
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
                )

            return SignInUser(id=str(user.id), email=user.email)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("User signin failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Signin operation failed",
            ) from e

    def update_password(self, data: UpdatePassword) -> Response[None]:
        """Update a user's password.

        Args:
            data: UpdatePassword model with user_id, old and new passwords.

        Returns:
            Response confirming successful password update.

        Raises:
            HTTPException: If user not found or old password incorrect.
        """
        try:
            user = self._user.get_user_by_id(data.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            if not self._password.verify_password(
                plain_password=data.old_password,
                hashed_password=user.password,
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Old password is incorrect",
                )

            user.password = self._password.get_hashed_password(data.new_password)
            self._db.commit()

            logger.info(f"Password updated for user id={user.id}")

            return Response[None](
                status=Status.success,
                message="Password updated successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Password update failed for user id={data.user_id}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            ) from e
