from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Response,
)
from app.schemas import response as custom_response
from app.schemas.db import auth, user as userschema
from app.utils.logger import get_logger
from app.services.db import user, sessions
from app.services.auth.password import get_hashed_password, verify_password
from datetime import datetime, timedelta
from app.config import config
from app.services.auth.token import (
    create_access_token,
    create_refresh_token,
    get_details_from_access_token,
    get_user_id_from_refresh_token,
)
from app.configs.database import SessionDep

router = APIRouter(prefix="/auth")

logger = get_logger(__name__)


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
def on_signup(
    data: userschema.UserCreate,
    request: Request,
    response: Response,
    session: SessionDep,
):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    try:
        logger.debug("Starting with user registration endpoint")
        logger.debug("Password hashing....")

        user_data = data.model_dump()
        user_data["password"] = get_hashed_password(data.password)

        logger.debug("Password hashed successfully")
        new_user = user.create_user(user=user_data, session=session)

        if not new_user.data["id"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register new user with email:{data.email}",
            )
        logger.debug(f"Successfully created the user with id:{new_user.data['id']}")
        logger.debug(
            f"started generating the refresh token for user id: {new_user.data['id']}"
        )
        payload = {
            "user_id": str(new_user.data["id"]),
            "email": new_user.data["email"],
            "name": new_user.data["name"],
        }

        refresh_token = create_refresh_token(payload)

        details = auth.SessionCreate(
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=new_user.data["id"],
            token=refresh_token,
            expires_at=datetime.now()
            + timedelta(days=int(config.REFRESH_TOKEN_EXPIRE_DAYS)),
        )
        sessions.create_session(details, session=session)
        logger.info(
            "successfully generated the refresh token and stored in the session"
        )
        access_token = create_access_token(payload)
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
            samesite="lax",
            max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return custom_response.Response(
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


@router.post("/sign-in", status_code=status.HTTP_200_OK)
def on_signin(
    data: auth.SignIn, request: Request, response: Response, session: SessionDep
):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    try:
        logger.debug("Starting sign in proccess for the user")

        old_user = user.get_user_by_email(email=data.email, session=session)
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

        payload = {
            "user_id": str(old_user.data["id"]),
            "email": old_user.data["email"],
            "name": old_user.data["name"],
        }
        new_refresh_token = create_refresh_token({"sub": payload})

        details = auth.SessionCreate(
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=old_user.id,
            token=new_refresh_token,
            expires_at=datetime.now()
            + timedelta(days=int(config.REFRESH_TOKEN_EXPIRE_DAYS)),
        )
        sessions.create_session(details, session=session)

        access_token = create_access_token({"sub": payload})
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            secure=False,  # True for production
            samesite="lax",  # none if frontend is deployed in another domain
            max_age=int(config.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
        )

        response.set_cookie(
            key="token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=int(config.REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 60 * 60,
        )

        return custom_response.Response(
            status="success", message="successfully logged in"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to log in the user {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signin",
        )


@router.delete("/sign-out", status_code=status.HTTP_200_OK)
def on_signout(request: Request, response: Response, session: SessionDep):
    try:
        logger.debug("Starting to sign out process")
        token_data = get_user_id_from_refresh_token(request=request)

        if token_data.user_id is None or token_data.token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid creadentials"
            )

        params = auth.GetSessionReq(user_id=token_data.user_id, token=token_data.token)
        old_session = sessions.get_session(data=params, session=session)

        if not old_session:
            sessions.remove_session(old_session=old_session, session=session)
            logger.debug("Successfully removed the session")

        response.delete_cookie(key="jwt")
        response.delete_cookie(key="token")
        return custom_response.Response(
            status="success", message="Successfully logged out"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log out the user {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during log out",
        )


@router.get("/refresh", status_code=status.HTTP_200_OK)
def on_token_refresh(request: Request, response: Response, session: SessionDep):
    try:
        logger.debug("Starting to refresh the token")
        token_data = get_user_id_from_refresh_token(request=request)

        if token_data.user_id is None and token_data.token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found"
            )

        params = auth.GetSessionReq(user_id=token_data.user_id, token=token_data.token)
        old_session = sessions.get_session(data=params, session=session)

        if not old_session:
            logger.error(
                f"Failed to found old session for the user_id:{token_data.user_id}"
            )
            raise HTTPException(
                detail="No user found", status_code=status.HTTP_401_UNAUTHORIZED
            )

        access_token = create_access_token({"sub": str(token_data.user_id)})
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            secure=False,  # True for production
            samesite="lax",  # none if frontend is deployed in another domain
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return custom_response.Response(
            status="success", message="Successfully refreshed"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to refresh to access token {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during refresh",
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def on_reset_password(request: Request, response: Response, session: SessionDep):
    pass


@router.get("/me", status_code=status.HTTP_200_OK)
def on_get_current_user(request: Request):
    token_data = get_details_from_access_token(request)
    return {"status": "success", "message": "Authenticated", "data": token_data}
