from fastapi import APIRouter, Depends, status, HTTPException
from app.models import Response, Status
from app.core import get_logger
from app.db import SessionDep
from app.services import get_user_service, UserService
from app.utils import  RefreshTokenUserId
from app.api.v1.auth import get_user_id

logger = get_logger(__name__)

user_router = APIRouter(prefix="/users")

@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=Response)
def get_current_user(
    session: SessionDep,
    user: RefreshTokenUserId = Depends(get_user_id),
):
    try:
        return Response(
            message="Successfully found the user",
            status=Status.success,
            data={"email": user.email, "user_id": user.user_id},
        )
    except HTTPException:
        raise


@user_router.delete("/me", status_code=status.HTTP_200_OK, response_model=Response)
def remove_current_user(
    session: SessionDep,
    user: RefreshTokenUserId = Depends(get_user_id),
    user_service: UserService = Depends(get_user_service),
):
    try:
        return user_service.delete_user(user_id=user.user_id)
    except HTTPException:
        raise
