from fastapi import APIRouter, Depends, status, Request
from app.models import Response
from app.core import get_logger
from app.db import SessionDep
from app.utils import TokenToUserId

logger = get_logger(__name__)

user_router = APIRouter(prefix="/users", tags=["user"])


def get_user_id(request: Request, session: SessionDep) -> dict[str, str]:
    user = TokenToUserId(session=session)
    old_user = user.get_user_id_from_refresh_token(request=request)
    return old_user


@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=Response)
def get_current_user(
    session: SessionDep, user_id: dict[str, str] = Depends(get_user_id)
): ...
