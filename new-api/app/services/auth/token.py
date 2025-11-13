from datetime import datetime, timedelta, timezone
from app.config import config
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request
from app.schemas.db.user import ResponseFromToken
from uuid import UUID


def create_access_token(data: dict) -> str:
    try:
        """Create a JWT access token with user_id"""
        if not data or "sub" not in data:
            raise ValueError("Token must have user_id field")

        if not config.ACCESS_TOKEN_EXPIRE_MINUTES and not config.SECRET_KEY:
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES and SECRET_KEY both needs to exists in the env"
            )

        to_encode = data.copy()
        expires_delta = int(config.ACCESS_TOKEN_EXPIRE_MINUTES)

        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire, "type": "access", "iat": datetime.now()})

        encoded_jwt = jwt.encode(
            to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )

        return encoded_jwt

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access token: {str(e)}",
        )


def create_refresh_token(data: dict) -> str:
    try:
        """Create a JWT refresh token with user_id"""
        if not data or "sub" not in data:
            raise ValueError("Token must have user_id field")

        if not config.REFRESH_TOKEN_EXPIRE_DAYS and not config.SECRET_KEY:
            raise ValueError(
                "REFRESH_TOKEN_EXPIRE_DAYS and SECRET_KEY both needs to exists in the env"
            )

        to_encode = data.copy()
        expires_delta = int(config.REFRESH_TOKEN_EXPIRE_DAYS)

        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)

        to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.now()})

        encode_jwt = jwt.encode(
            to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
        )

        return encode_jwt

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating refresh token: {str(e)}",
        )


def get_user_id_from_access_token(request: Request) -> UUID:
    """Extract user id from the access token"""
    token = request.cookies.get("jwt")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        if not config.SECRET_KEY:
            raise ValueError("SECRET_KEY missing in the env")
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    return user_id


def get_user_id_from_refresh_token(request: Request) -> ResponseFromToken:
    """Extract user id from the refresh token"""
    token = request.cookies.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        if not config.SECRET_KEY:
            raise ValueError("SECRET_KEY missing in the env")
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    return ResponseFromToken(user_id=user_id, token=token)
