from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_hashed_password(password: str) -> str:
    """Hash a password with error handling"""
    try:
        if not password:
            raise ValueError("Password cannot be empty")
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error hashing password: {str(e)}",
        )
