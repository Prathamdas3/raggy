from uuid import UUID, uuid4
from app.core import AppException, get_logger, config
from app.repository import ChatRepo,ReturnChatType
from app.models import UpdateChat
from app.schemas import Chats

logger = get_logger(__name__)


class ChatService:
    def __init__(self, repo:ChatRepo):
        self._repo = repo

    def find_chat(self, chat_id: UUID,user_id:UUID) -> Chats:
        chat = self._repo.get_by_id(chat_id,user_id)
        if not chat:
            raise AppException(status_code=404, message="Chat not found")
        return chat
    
    def get_chats(self, user_id: UUID) -> list[ReturnChatType]:
        return self._repo.get_chats(user_id)

    def create_chat(self, user_id: UUID, title: str, original_doc: str) -> UUID:
        chat = self._repo.create_chat(user_id, title, original_doc)
        return chat.id

    def remove_chat(self, chat_id: UUID,user_id:UUID) -> str:
        chat = self.find_chat(chat_id,user_id)
        self._repo.delete(chat)
        return "Successfully removed the chat"

    def update_chat(self, data: UpdateChat) -> str:
        if not data.has_update():
            raise AppException(status_code=400, message="No content to update")
        chat = self.find_chat(data.chat_id,data.user_id)
        for field, value in data.model_dump(exclude_unset=True, exclude={"chat_id"}).items():
            setattr(chat, field, value)
        self._repo.save(chat)
        return "Successfully updated the chat"

    def share_chat(self, chat_id: UUID,user_id:UUID) -> str:
        chat = self.find_chat(chat_id,user_id)
        if chat.share_id:
            return f"{config.frontend_url}/{chat.share_id}"
        chat.share_id = str(uuid4())
        self._repo.save(chat)
        return f"{config.frontend_url}/{chat.share_id}"

    def create_branch(self, chat_id: UUID,user_id:UUID, parent_branch_id: UUID | None = None) -> UUID:
        self.find_chat(chat_id,user_id)  # validates chat exists
        branch = self._repo.create_branch(chat_id, parent_branch_id)
        return branch.id