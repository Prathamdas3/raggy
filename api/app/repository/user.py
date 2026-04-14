from uuid import UUID
from sqlmodel import select,Session
from app.schemas import Users


class UserRepo:
    def __init__(self, session: Session):
        self._db = session

    def get_by_id(self, user_id: UUID) -> Users | None:
        return self._db.get(Users, user_id)

    def get_by_email(self, email: str) -> Users | None:
        return self._db.exec(
            select(Users).where(Users.email == email)
        ).first()

    def save(self, instance: Users) -> Users:
        self._db.add(instance)
        self._db.commit()
        self._db.refresh(instance)
        return instance

    def delete(self, instance: Users) -> None:
        self._db.delete(instance)
        self._db.commit()
