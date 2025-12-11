from passlib.context import CryptContext
from fastapi import HTTPException, status

# Configure passlib to use bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  
)


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
        
        # Bcrypt has a 72-byte limit - truncate if needed
        # This is safe because we validate minimum length above
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            # Truncate to 72 bytes
            password = password_bytes[:72].decode("utf-8", errors="ignore")
        
        return pwd_context.hash(password)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing password: {str(e)}",
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to check against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Apply same truncation logic as hashing
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode("utf-8", errors="ignore")
        
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False