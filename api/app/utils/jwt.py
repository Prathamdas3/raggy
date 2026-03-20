"""JWT token utilities.

Provides JWT class for creating access and refresh tokens,
and TokenToUserId for extracting user information from tokens.
"""

from pydantic import EmailStr
from sqlmodel import Session
from dataclasses import dataclass

from app.core.logger import get_logger
from app.models.jwt import Tokens
from app.db.schema import Users
from app.core.config import config
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request
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
            HTTPException: If token creation fails.
        """
        try:
            to_encode = self.payload.copy()
            expires_data = config.access_token_expire_minutes

            if expires_data:
                expire = datetime.now(timezone.utc) + timedelta(minutes=expires_data)
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=15)

            to_encode.update({"exp": expire, "type": "access", "iat": datetime.now()})

            encoded_jwt = jwt.encode(
                to_encode, config.secret_key, algorithm=config.algorithm
            )

            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create jwt: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to form jwt",
            )

    def create_refresh_token(self) -> str:
        """Create a JWT refresh token with user_id and email.

        Returns:
            Encoded JWT refresh token string.

        Raises:
            HTTPException: If token creation fails.
        """
        try:
            to_encode = self.payload.copy()
            expires_data = config.refresh_token_expire_days

            if expires_data:
                expire = datetime.now(timezone.utc) + timedelta(days=expires_data)
            else:
                expire = datetime.now(timezone.utc) + timedelta(days=7)

            to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.now()})

            encoded_jwt = jwt.encode(
                to_encode, config.secret_key, algorithm=config.algorithm
            )

            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to form token",
            )


class TokenToUserId:
    """Token validation and user extraction utility.

    Provides methods for extracting and validating user information
    from JWT tokens.
    """

    def __init__(self, session: Session):
        """Initialize TokenToUserId with database session.

        Args:
            session: SQLModel session for user lookup.
        """
        self._db = session

    def _get_user_by_id(self, old_user_id: str) -> Users:
        """Fetch user by ID and raise if not found.

        Args:
            old_user_id: String representation of user UUID.

        Returns:
            User entity.

        Raises:
            ValueError: If user_id is empty.
            TypeError: If user_id is not a valid UUID.
            HTTPException: If user not found or database error.
        """
        if not old_user_id:
            raise ValueError("No user id provided")

        try:
            user_id: UUID = UUID(old_user_id)
        except Exception:
            raise TypeError("user_id must be a valid uuid")

        try:
            user = self._db.get(Users, user_id)
            if user is None:
                logger.warning(f"User not found: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or invalid",
                )
            return user
        except Exception as e:
            logger.error(
                f"Database error fetching user {user_id}: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during user validation",
            ) from e

    def get_user_id_from_access_token(self, request: Request) -> str:
        """Extract user id from the access token.

        Args:
            request: FastAPI request object.

        Returns:
            String representation of user UUID.

        Raises:
            HTTPException: If token is invalid or user not found.
        """
        token = request.cookies.get("jwt")

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found "
            )

        try:
            payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if user_id is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            user_id = str(user_id)  # Safe cast since checked not None

            # Verify user exists in database
            self._get_user_by_id(user_id)

        except JWTError as je:
            logger.error(
                f"Failed to fetch the credentials from the access_token:{str(je)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        except Exception as e:
            logger.error(
                f"Failed to extract the user id from the access token: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate the user details",
            )

        return user_id

    def get_user_id_from_refresh_token(self, request: Request) -> RefreshTokenUserId:
        """Extract user id from the refresh token.

        Args:
            request: FastAPI request object.

        Returns:
            RefreshTokenUserId containing user_id, email, and token.

        Raises:
            HTTPException: If token is invalid or user not found.
        """
        token = request.cookies.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
            )

        try:
            payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
            user_id = payload.get("user_id")
            email = payload.get("email")
            token_type = payload.get("type")

            if user_id is None or email is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            user_id = str(user_id)
            email = str(email)

            # Verify user exists in database
            self._get_user_by_id(user_id)
        except HTTPException:
            raise
        except JWTError as je:
            logger.error(
                f"Failed to fetch the credentials from the refresh token: {str(je)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        except Exception as e:
            logger.error(
                f"Failed to extract the user id from the refresh token: {str(e)}",
                exc_info=True,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate the user details",
            )

        return RefreshTokenUserId(user_id=UUID(user_id), email=email, token=token)
