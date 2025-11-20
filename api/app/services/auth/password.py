from passlib.context import CryptContext
from fastapi import HTTPException, status
import hashlib

# Configure CryptContext with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Adjust rounds for security/performance balance
)


def _prepare_password(password: str) -> str:
    """
    Prepare password for bcrypt hashing.
    Bcrypt has a 72-byte limit, so we pre-hash long passwords with SHA-256.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    # If password is longer than 72 bytes, pre-hash it
    if len(password.encode("utf-8")) > 72:
        # Use SHA-256 to create a fixed-length hash
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        if not plain_password or not hashed_password:
            return False

        # Prepare password (handle 72-byte limit)
        prepared_password = _prepare_password(plain_password)

        return pwd_context.verify(prepared_password, hashed_password)
    except Exception:
        # Log the error in production

        return False


def get_hashed_password(password: str) -> str:
    """
    Hash a password with error handling.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password

    Raises:
        HTTPException: If password is invalid or hashing fails
    """
    try:
        if not password:
            raise ValueError("Password cannot be empty")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Prepare password (handle 72-byte limit)
        prepared_password = _prepare_password(password)

        return pwd_context.hash(prepared_password)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password",
        )
