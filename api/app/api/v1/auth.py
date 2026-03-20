"""Authentication API endpoints.

Provides endpoints for user registration (sign-up), authentication (sign-in),
logout, and token refresh operations.
"""

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Response as HttpResponse,
    Request,
)
from app.core import config, get_logger
from app.db import SessionDep
from app.models import Response, Status, CreateUser, SigninUser, Tokens
from app.services import AuthService, get_auth_service
from app.utils import JWT, TokenToUserId, RefreshTokenUserId


logger = get_logger(__name__)
auth_router = APIRouter(prefix="/auth")


def get_tokens(payload: Tokens):
    """Create JWT tokens from payload.

    Args:
        payload: Token payload containing user_id and email.

    Returns:
        JWT instance with encoded tokens.
    """
    return JWT(payload=payload)


def get_user_id(request: Request, session: SessionDep) -> RefreshTokenUserId:
    """Extract user ID from refresh token.

    Args:
        request: FastAPI request object.
        session: Database session.

    Returns:
        RefreshTokenUserId containing user_id and email.
    """
    user = TokenToUserId(session=session)
    old_user: RefreshTokenUserId = user.get_user_id_from_refresh_token(request=request)
    return old_user


def set_cookies(response: HttpResponse, key: str, value: str, time: int, type: str):
    """Set HTTP-only cookies for token storage.

    Args:
        response: HTTP response object.
        key: Cookie name.
        value: Cookie value (JWT token).
        time: Expiration time value.
        type: Time unit ('days' or 'mins').
    """
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=time * 24 * 60 * 60 if type == "days" else time * 60,
    )


@auth_router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=Response,
)
def handle_signup(
    data: CreateUser,
    response: HttpResponse,
    auth: AuthService = Depends(get_auth_service),
) -> dict[str, str | Status | dict[str, str]]:
    """Register a new user account.

    Args:
        data: User registration data (email and password).
        response: HTTP response for setting cookies.
        auth: Authentication service dependency.

    Returns:
        Response with user info and JWT tokens.

    Raises:
        HTTPException: If user creation or token generation fails.
    """
    try:
        user = auth.user_signup(data=data)

        if not user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create the user",
            )

        payload = Tokens(user_id=str(user["id"]), email=user["email"])
        tokens = get_tokens(payload=payload)

        access_token = tokens.create_access_token()
        refresh_token = tokens.create_refresh_token()

        if not access_token or not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tokens",
            )

        set_cookies(
            response=response,
            key="jwt",
            value=access_token,
            type="mins",
            time=config.access_token_expire_minutes,
        )
        set_cookies(
            response=response,
            key="token",
            value=refresh_token,
            type="days",
            time=config.refresh_token_expire_days,
        )

        return {
            "message": "Successfully created the user",
            "status": Status.success,
            "data": {"id": user["id"], "email": user["email"]},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup",
        )


@auth_router.post("/sign-in", status_code=status.HTTP_200_OK, response_model=Response)
def handle_signin(
    data: SigninUser,
    response: HttpResponse,
    auth: AuthService = Depends(get_auth_service),
) -> Response:
    """Authenticate an existing user.

    Args:
        data: User sign-in credentials (email and password).
        response: HTTP response for setting cookies.
        auth: Authentication service dependency.

    Returns:
        Response with user info and JWT tokens.

    Raises:
        HTTPException: If authentication or token generation fails.
    """
    try:
        result = auth.user_signin(data=data)

        if not result.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sign in the user",
            )

        payload = Tokens(user_id=str(result.id), email=result.email)
        tokens = get_tokens(payload=payload)

        access_token = tokens.create_access_token()
        refresh_token = tokens.create_refresh_token()

        if not access_token or not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tokens",
            )

        set_cookies(
            response=response,
            key="jwt",
            value=access_token,
            type="mins",
            time=config.access_token_expire_minutes,
        )
        set_cookies(
            response=response,
            key="token",
            value=refresh_token,
            type="days",
            time=config.refresh_token_expire_days,
        )

        return Response(
            message="Successfully signed in", status=Status.success, data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signin",
        )


@auth_router.delete(
    "/sign-out", status_code=status.HTTP_200_OK, response_model=Response
)
def handle_logout(
    request: Request,
    response: HttpResponse,
    user: RefreshTokenUserId = Depends(get_user_id),
) -> Response:
    """Sign out the current user.

    Clears authentication cookies and invalidates the session.

    Args:
        request: FastAPI request object.
        response: HTTP response for clearing cookies.
        user: Authenticated user from refresh token.

    Returns:
        Response confirming successful logout.

    Raises:
        HTTPException: If credentials are invalid or logout fails.
    """
    try:
        if not user.user_id or not user.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        response.delete_cookie(key="jwt")
        response.delete_cookie(key="token")

        return Response(message="Successfully signed out", status=Status.success)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout",
        )


@auth_router.get("/refresh", status_code=status.HTTP_200_OK, response_model=Response)
def handle_refresh(
    request: Request,
    response: HttpResponse,
    user: RefreshTokenUserId = Depends(get_user_id),
) -> Response:
    """Refresh the access token using refresh token.

    Args:
        request: FastAPI request object.
        response: HTTP response for setting new cookies.
        user: Authenticated user from refresh token.

    Returns:
        Response with new access token.

    Raises:
        HTTPException: If token refresh fails.
    """
    try:
        if not user.user_id or not user.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
            )

        payload = Tokens(user_id=str(user.user_id), email=user.email)
        tokens = get_tokens(payload=payload)
        access_token = tokens.create_access_token()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tokens",
            )
        set_cookies(
            response=response,
            key="jwt",
            value=access_token,
            type="mins",
            time=config.access_token_expire_minutes,
        )
        return Response(message="Token refreshed", status=Status.success)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signin",
        )
