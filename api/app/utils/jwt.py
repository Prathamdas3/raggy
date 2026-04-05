"""JWT token utilities.

Provides JWT class for creating access and refresh tokens,
and TokenToUserId for extracting user information from tokens.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr
from dataclasses import dataclass

from app.core.logger import get_logger
from app.models.jwt import Tokens
from app.db.schemas import Users
from app.core.config import config
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import status, Request
from app.core import AppException
from uuid import UUID

logger = get_logger(__name__)


@dataclass
class RefreshTokenUserId:
    """Data class containing user info extracted from refresh token.

    Attributes:
        user_id: UUID of the user.
        email: User's email address.
        token: The refresh token string.
    """

    user_id: UUID
    email: EmailStr
    token: str


class JWT:
    """JWT token creation utility.

    Provides methods for creating access and refresh tokens
    with configurable expiration times.
    """

    def __init__(self, payload: Tokens):
        """Initialize JWT with token payload.

        Args:
            payload: Token payload containing user_id and email.
        """
        self.payload = payload.model_dump()

    def create_access_token(self) -> str:
        """Create a JWT access token with user_id and email.

        Returns:
            Encoded JWT access token string.

        Raises:
            AppException: If token creation fails.
        """
        try:
            to_encode = self.payload.copy()
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.access_token_expire_minutes or 15
            )
            to_encode.update(
                {"exp": expire, "type": "access", "iat": datetime.now(timezone.utc)}
            )

            encoded_jwt = jwt.encode(
                to_encode, config.secret_key, algorithm=config.algorithm
            )

            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create jwt: {str(e)}")
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to form jwt",
            )

    def create_refresh_token(self) -> str:
        """Create a JWT refresh token with user_id and email.

        Returns:
            Encoded JWT refresh token string.

        Raises:
            AppException: If token creation fails.
        """
        try:
            to_encode = self.payload.copy()

            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.refresh_token_expire_days or 15 * 24 * 60
            )

            to_encode.update(
                {"exp": expire, "type": "refresh", "iat": datetime.now(timezone.utc)}
            )

            encoded_jwt = jwt.encode(
                to_encode, config.secret_key, algorithm=config.algorithm
            )

            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create token: {str(e)}")
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to form token",
            )


class TokenToUserId:
    """Token validation and user extraction utility.

    Provides methods for extracting and validating user information
    from JWT tokens.
    """

    def __init__(self, session: AsyncSession):
        """Initialize TokenToUserId with database session.

        Args:
            session: SQLModel session for user lookup.
        """
        self._db = session

    async def _get_user_by_id(self, old_user_id: str) -> Users:
        """Fetch user by ID and raise if not found.

        Args:
            old_user_id: String representation of user UUID.

        Returns:
            User entity.

        Raises:
            ValueError: If user_id is empty.
            TypeError: If user_id is not a valid UUID.
            AppException: If user not found or database error.
        """
        if not old_user_id:
            raise ValueError("No user id provided")

        try:
            user_id: UUID = UUID(old_user_id)
        except Exception:
            raise TypeError("user_id must be a valid uuid")

        try:
            user = await self._db.get(Users, user_id)
            if user is None:
                logger.warning(f"User not found: {user_id}")
                raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    message="User not found or invalid",
                )
            return user
        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"Database error fetching user {user_id}: {str(e)}",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Database error during user validation",
            ) from e

    async def get_user_id_from_access_token(self, request: Request) -> str:
        """Extract user id from the access token.

        Args:
            request: FastAPI request object.

        Returns:
            String representation of user UUID.

        Raises:
            AppException: If token is invalid or user not found.
        """
        token = request.cookies.get("jwt")

        if not token:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED, message="No user found "
            )

        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.algorithm]
            )
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if user_id is None or token_type != "access":
                raise AppException(
                    status_code=status.HTTP_401_UNAUTHORIZED, message="Invalid token"
                )

            user_id = str(user_id)  # Safe cast since checked not None

            # Verify user exists in database
            await self._get_user_by_id(user_id)

        except AppException:
            raise
        except JWTError as je:
            logger.error(
                f"Failed to fetch the credentials from the access_token:{str(je)}",
            )
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Could not validate credentials",
            )
        except Exception as e:
            logger.error(
                f"Failed to extract the user id from the access token: {str(e)}",
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to validate the user details",
            )

        return user_id

    async def get_user_id_from_refresh_token(
        self, request: Request
    ) -> RefreshTokenUserId:
        """Extract user id from the refresh token.

        Args:
            request: FastAPI request object.

        Returns:
            RefreshTokenUserId containing user_id, email, and token.

        Raises:
            AppException: If token is invalid or user not found.
        """
        token = request.cookies.get("token")
        if not token:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED, message="No user found"
            )

        try:
            payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
            user_id = payload.get("user_id")
            email = payload.get("email")
            token_type = payload.get("type")

            if user_id is None or email is None or token_type != "refresh":
                raise AppException(
                    status_code=status.HTTP_401_UNAUTHORIZED, message="Invalid token"
                )

            user_id = str(user_id)
            email = str(email)

            # Verify user exists in database
            await self._get_user_by_id(user_id)
        except AppException:
            raise
        except JWTError as je:
            logger.error(
                f"Failed to fetch the credentials from the refresh token: {str(je)}",
            )
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Could not validate credentials",
            )
        except Exception as e:
            logger.error(
                f"Failed to extract the user id from the refresh token: {str(e)}",
            )

            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to validate the user details",
            )

        return RefreshTokenUserId(user_id=UUID(user_id), email=email, token=token)
