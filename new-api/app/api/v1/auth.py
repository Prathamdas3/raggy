from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Response as ResponseFastAPI,
)
from app.schemas import user as userschema, auth
from app.schemas.response import Response
from app.utils.logger import get_logger
from app.services import user, sessions
from app.utils.password import get_hashed_password, verify_password
from app.schemas.auth import SessionCreate, GetSessionReq
from datetime import datetime, timedelta
from app.config import config
from app.utils.token import (
    create_access_token,
    create_refresh_token,
    get_user_id_from_refresh_token,
)

router = APIRouter(prefix="/auth")

logger = get_logger(__name__)


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
def on_signup(data: userschema.UserCreate, request: Request, response: ResponseFastAPI):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    try:
        logger.debug("Starting with user registration endpoint")

        logger.debug("Password hashing....")

        user_data = data.model_dump()
        user_data["password"] = get_hashed_password(data.password)

        logger.debug("Password hashed successfully")

        new_user = user.create_user(user=user_data)

        if not getattr(new_user, "id", None):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register new user with email:{data.email}",
            )
        logger.debug(f"Successfully created the user with id:{new_user.data.id}")
        logger.debug(
            f"started generating the refresh token for user id: {new_user.data.id}"
        )
        refresh_token = create_refresh_token({"sub": str(new_user.data.id)})

        details = SessionCreate(
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=new_user.data.id,
            token=refresh_token,
            expires_at=datetime.now()
            + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        sessions.create_session(details)
        logger.info(
            "successfully generated the refresh token and stored in the session"
        )
        access_token = create_access_token({"sub": str(new_user.data.id)})
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            secure=False,  # True for production
            samesite="lax",  # none if frontend is deployed in another domain
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="none",
            max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return Response(
            message="successfully created the user",
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create the user {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signup",
        )


@router.post("/sign_in", status_code=status.HTTP_200_OK)
def on_signin(request: Request, response: ResponseFastAPI, data: auth.SignIn):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    try:
        logger.debug("Starting sign in proccess for the user")

        old_user = user.get_user_by_email(email=data.email)
        if not old_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No user found with this email",
            )

        old_password = old_user.password
        check_password = verify_password(
            plain_password=data.password, hashed_password=old_password
        )

        if not check_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
            )

        new_refresh_token = create_refresh_token({"sub": str(old_user.id)})

        details = SessionCreate(
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=old_user.id,
            token=new_refresh_token,
            expires_at=datetime.now()
            + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        sessions.create_session(details)

        access_token = create_access_token({"sub": str(old_user.id)})
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            secure=False,  # True for production
            samesite="lax",  # none if frontend is deployed in another domain
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="none",
            max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return Response(status="success", message="successfully logged in")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to log in the user {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signin",
        )


@router.delete("/sign_out", status_code=status.HTTP_200_OK)
def on_signout(request: Request, response: ResponseFastAPI):
    try:
        logger.debug("Starting to sign out process")
        user_id, token = get_user_id_from_refresh_token(request=request)

        if not user_id or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid creadentials"
            )

        params = GetSessionReq(user_id=user_id, token=token)
        old_session = sessions.get_session(data=params)

        if not old_session:
            sessions.remove_session(old_session=old_session)
            logger.debug("Successfully removed the session")

        response.delete_cookie(key="jwt")
        response.delete_cookie(key="token")
        return Response(status="Success", message="Successfully logged out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log out the user {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signin",
        )


@router.get("/refresh", status_code=status.HTTP_200_OK)
def on_token_refresh(request: Request, response: ResponseFastAPI):
    try:
        logger.debug("Starting to refresh the token")
        user_id, token = get_user_id_from_refresh_token(request=request)
        if not user_id or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
            )

        params = GetSessionReq(user_id=user_id, token=token)
        old_session = sessions.get_session(data=params)
        if not old_session:
            raise HTTPException(
                detail="No user found", status_code=status.HTTP_401_UNAUTHORIZED
            )

        access_token = create_access_token({"sub": str(user_id)})
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            secure=False,  # True for production
            samesite="lax",  # none if frontend is deployed in another domain
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return Response(status="success", message="Successfully refreshed")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to refresh to access token {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signin",
        )
