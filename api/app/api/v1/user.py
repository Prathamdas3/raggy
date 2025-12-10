from fastapi import APIRouter, status, HTTPException, Depends
from app.configs.rate_limiter import rate_limit_default
from app.schemas.db.user import UpdateUser, UpdatePassword, UpdatePasswordInput
from app.schemas.response import Response
from app.services.auth.token import get_user_id_from_access_token
from app.services.db.user import (
    update_user_details as update_details,
    update_user_password as update_password,
)
from app.services.db.user import get_user_by_id
from app.utils.logger import get_logger
from app.configs.database import SessionDep
from uuid import UUID

router = APIRouter(prefix="/user")

logger = get_logger(__name__)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def get_user(
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        logger.debug("Getting the user with the user id ")
        user = get_user_by_id(user_id=user_id, session=session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No user found"
            )
        logger.debug(f"User found with the id: {user.id}")
        return Response(
            status="success",
            message="Successfully fetched the user",
            data={
                "id": user.id,
                "user_name": user.user_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to fetch the user with the user id: {user.id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the user details",
        )


@router.patch(
    "/update-details",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def update_user_details(
    session: SessionDep,
    data: UpdateUser,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    logger.debug("Starting to update the user details")
    try:
        update_details(details=data, user_id=user_id, session=session)
        return Response(
            status="success", message="Successfully updated the details of the user"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update the user details:{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update the user details",
        )


@router.patch(
    "/update-password",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def update_user_password(
    session: SessionDep,
    data: UpdatePasswordInput,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    logger.debug(f"Starting to update the password of user with the user_id: {user_id}")

    try:
        new_details = UpdatePassword(
            user_id=user_id,
            old_password=data.old_password,
            new_password=data.new_password,
        )

        update_password(data=new_details, session=session)
        return Response(status="success", message="Successfully updated the password")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update the user password:{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update the user with new user password",
        )
