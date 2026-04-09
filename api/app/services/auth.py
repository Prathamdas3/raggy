"""Authentication service for user sign-up and sign-in.

This module provides the AuthService class that handles user registration,
login, and password update operations.
"""

from dataclasses import dataclass
from fastapi import status
from pydantic import EmailStr


from app.core import get_logger
from app.models import CreateUser, SigninUser, UpdatePassword
from app.schemas import Users
from app.utils import HandlePassword
from app.core import AppException
from app.repository import UserRepo

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
        self,
        repo: UserRepo,
        password: HandlePassword,
    ):
        """Initialize AuthService with dependencies.

        Args:
            db_service: Database service instance.
            password: Password handler for hashing/verification.
            user: FindUser service for user lookup.
        """
        self._repo = repo
        self._password = password

    def user_signup(self, data: CreateUser)->SignInUser:
        """Register a new user.

        Args:
            data: CreateUser model with email and password.

        Returns:
            Dictionary with created user's id and email.

        Raises:
            AppException: If email already exists or signup fails.
        """
        existing = self._repo.get_by_email(data.email)
        if existing:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                message="Email already exists",
            )

        hashed_password = self._password.get_hashed_password(data.password)

        new_user = Users(email=data.email, password=hashed_password)
        self._repo.save(instance=new_user)

        logger.info(f"User created with id={new_user.id}")

        return SignInUser(id= str(new_user.id), email= new_user.email)

    def user_signin(self, data: SigninUser) -> SignInUser:
        """Authenticate a user with email and password.

        Args:
            data: SigninUser model with email and password.

        Returns:
            SignInUser with authenticated user's id and email.

        Raises:
            AppException: If user not found or password incorrect.
        """
        user = self._repo.get_by_email(data.email)
        if not user:
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="No user found with the given email",
                )

        old_password = user.password
        new_password = data.password

        if not self._password.verify_password(
                plain_password=new_password, hashed_password=old_password
            ):
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Incorrect password",
                )

        return SignInUser(id=str(user.id), email=user.email)


    def update_password(self, data: UpdatePassword) -> str:
        """Update a user's password.

        Args:
            data: UpdatePassword model with user_id, old and new passwords.

        Returns:
            Response confirming successful password update.

        Raises:
            AppException: If user not found or old password incorrect.
        """
        user = self._repo.get_by_id(data.user_id)
        if not user:
            raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="User not found",
                )

        if not self._password.verify_password(
                plain_password=data.old_password,
                hashed_password=user.password,
            ):
            raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    message="Old password is incorrect",
                )

        user.password = self._password.get_hashed_password(data.new_password)
        self._repo.save(instance=user)

        logger.info(f"Password updated for user id={user.id}")

        return "Password updated successfully"


