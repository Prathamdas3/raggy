"""Authentication API endpoints.

Provides endpoints for user registration (sign-up), authentication (sign-in),
logout, and token refresh operations.
"""

from fastapi import (
    APIRouter,
    status,
    Response as HttpResponse,
    Request,
)
from app.core import config, get_logger, AppException
from app.models import Response, CreateUser, SigninUser, Tokens
from app.services import AuthServiceDep
from app.utils import create_access_token, create_refresh_token,CurrentUserDep,CurrentUserRefreshDep


logger = get_logger(__name__)
auth_router = APIRouter(prefix="/auth")


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
        secure=config.env == "production",
        samesite="lax",
        max_age=time * 24 * 60 * 60 if type == "days" else time * 60,
    )


def create_auth_tokens(payload: Tokens) -> tuple[str, str]:
    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(payload=payload)

    if not access_token or not refresh_token:
        raise AppException(message="Failed to generate tokens.",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return access_token, refresh_token


@auth_router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=Response,
)
def handle_signup(
    data: CreateUser,
    response: HttpResponse,
    auth: AuthServiceDep,
) -> dict[str, dict[str,str]]:
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

    user =auth.user_signup(data=data)
    access_token, refresh_token = create_auth_tokens(
        Tokens(user_id=str(user.id), email=user.email)
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

    return {"data": {"id": user.id, "email": user.email}}


@auth_router.post("/sign-in", status_code=status.HTTP_200_OK, response_model=Response)
def handle_signin(
    data: SigninUser,
    response: HttpResponse,
    auth: AuthServiceDep,
) -> dict[str, dict[str,str]]:
    user = auth.user_signin(data=data)
    access_token, refresh_token = create_auth_tokens(
        Tokens(user_id=str(user.id), email=user.email)
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
        "data": {
            "id": user.id,
            "email": user.email,
        }
    }


@auth_router.delete(
    "/sign-out", status_code=status.HTTP_200_OK, response_model=Response
)
def handle_logout(
    request: Request,
    response: HttpResponse,
    _user: CurrentUserDep,
) -> dict[str, str]:
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

    response.delete_cookie(key="jwt")
    response.delete_cookie(key="token")

    return {"data": "Successfully signed out"}


@auth_router.get("/refresh", status_code=status.HTTP_200_OK, response_model=Response)
def handle_refresh(
    request: Request,
    response: HttpResponse,
    user: CurrentUserRefreshDep,
) -> dict[str, str]:
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


    payload = Tokens(user_id=str(user.user_id), email=user.email)
    access_token,_ = create_auth_tokens(payload=payload)
        
    set_cookies(
            response=response,
            key="jwt",
            value=access_token,
            type="mins",
            time=config.access_token_expire_minutes,
        )
    return {"data": "Token refreshed"}
