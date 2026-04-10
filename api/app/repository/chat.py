from typing import cast, TypedDict
from uuid import UUID
from sqlmodel import select
from sqlmodel import Session
from app.schemas import Chats, ChatBranches


class ReturnChatType(TypedDict):
    """Type definition for chat list return values."""

    title: str
    is_bookmarked: bool
    created_at: str


class ChatRepo:
    def __init__(self, session: Session):
        self._db = session

    def get_by_id(self, chat_id: UUID, user_id: UUID) -> Chats | None:
        return self._db.exec(
            select(Chats).where(Chats.id == chat_id, Chats.user_id == user_id)
        ).first()

    def get_chats(self, user_id: UUID) -> list[ReturnChatType]:
        chats = self._db.exec(
           select(Chats).where(Chats.user_id == user_id)
        ).fetchall()
        if not chats:
            return []
        return cast(list[ReturnChatType], chats)

    def save(self, instance: Chats) -> Chats:
        self._db.add(instance)
        self._db.commit()
        self._db.refresh(instance)
        return instance

    def delete(self, instance: Chats) -> None:
        self._db.delete(instance)
        self._db.commit()

    def create_chat(self, user_id: UUID, title: str, original_doc: str) -> Chats:
        chat = Chats(user_id=user_id, title=title, original_doc=original_doc)
        self._db.add(chat)
        self._db.flush()
        branch = ChatBranches(chat_id=chat.id)
        self._db.add(branch)
        self._db.flush()
        chat.active_branch_id = branch.id
        self._db.commit()
        self._db.refresh(chat)
        return chat

    def create_branch(
        self, chat_id: UUID, parent_branch_id: UUID | None
    ) -> ChatBranches:
        branch = ChatBranches(chat_id=chat_id, parent_branch_id=parent_branch_id)
        self._db.add(branch)
        self._db.commit()
        self._db.refresh(branch)
        return branch
