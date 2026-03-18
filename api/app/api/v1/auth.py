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
    return JWT(payload=payload)


def get_user_id(request: Request, session: SessionDep) -> RefreshTokenUserId:
    user = TokenToUserId(session=session)
    old_user: RefreshTokenUserId = user.get_user_id_from_refresh_token(request=request)
    return old_user


def set_cookies(response: HttpResponse, key: str, value: str, time: int, type: str):
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
