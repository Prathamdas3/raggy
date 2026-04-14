from uuid import UUID
from sqlmodel import Session
from app.schemas import MessageRevisions, Messages


class MessageRepo:
    def __init__(self, session: Session):
        self._db = session

    def create(
        self,
        role,
        branch_id,
        sender_id=None,
        reply_to_message_id=None,
        content="",
        audio_url="",
    ) -> Messages:
        message = Messages(
            role=role,
            branch_id=branch_id,
            sender_id=sender_id,
            reply_to_message_id=reply_to_message_id,
        )
        self._db.add(message)
        self._db.flush()

        revision = MessageRevisions(
            message_id=message.id,
            content=content,
            edited_by=sender_id,
            audio_url=audio_url,
        )

        self._db.add(revision)
        self._db.commit()
        self._db.refresh(message)

        return message

    def update(self, message_id, content, audio_url, edited_by):
        revision = MessageRevisions(
            message_id=message_id,
            edited_by=edited_by,
            content=content,
           audio_url=audio_url
        )
        self._db.add(revision)
        self._db.commit()
        
