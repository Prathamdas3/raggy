from uuid import UUID
from app.core import AppException, get_logger
from app.models import CreateUser, UpdateUser
from app.schemas import Users
from app.utils import HandlePassword

logger = get_logger(__name__)


class UserService:
    def __init__(self, repo, password: HandlePassword):
        self._repo = repo
        self._password = password

    def _find_user(self, user_id: UUID) -> Users:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise AppException(status_code=404, message="User not found")
        return user

    def get_current_user(self, user_id: UUID) -> Users:
        return self._find_user(user_id)

    def create_user(self, data: CreateUser) -> dict[str, str]:
        existing = self._repo.get_by_email(data.email)
        if existing:
            raise AppException(status_code=409, message="Email already exists")
        hashed = self._password.get_hashed_password(data.password)
        user = Users(email=data.email, password=hashed)
        saved = self._repo.save(user)
        return {"id": str(saved.id), "email": saved.email}

    def update_user(self, user_id: UUID, data: UpdateUser) -> Users:
        if not data.has_updates():
            raise AppException(status_code=400, message="No fields to update")
        user = self._find_user(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return self._repo.save(user)

    def delete_user(self, user_id: UUID) -> str:
        user = self._find_user(user_id)
        self._repo.delete(user)
        return "User deleted successfully"