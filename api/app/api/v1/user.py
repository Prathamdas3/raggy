"""User API endpoints.

Provides endpoints for retrieving and managing the current authenticated user.
"""

from fastapi import APIRouter,  status, Response as HttpResponse
from app.models import Response
from app.core import get_logger
from app.services import UserServiceDep
from app.utils import CurrentUserDep


logger = get_logger(__name__)

user_router = APIRouter(prefix="/users",tags=["users"])


@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=Response)
def get_current_user(
    user: CurrentUserDep,
) -> dict[str, dict[str, str]]:
    """Get the current authenticated user.

    Args:
        session: Database session dependency.
        user: Authenticated user from refresh token.

    Returns:
        Response with user email and ID.

    Raises:
        HTTPException: If user lookup fails.
    """
    return {"data": {"email": user.email, "user_id": str(user.user_id)}}


@user_router.delete("/me", status_code=status.HTTP_200_OK, response_model=Response)
def remove_current_user(
    response: HttpResponse,
    user: CurrentUserDep,
    user_service: UserServiceDep,
)-> dict[str, str]:
    """Delete the current authenticated user.

    Args:
        session: Database session dependency.
        user: Authenticated user from refresh token.
        user_service: User service dependency.

    Returns:
        Response confirming successful deletion.

    Raises:
        HTTPException: If user deletion fails.
    """
    data=user_service.delete_user(user_id=user.user_id)
    response.delete_cookie(key="jwt")
    response.delete_cookie(key="token")
    return {"data": data}
    