from uuid import UUID
from app.core import celery,get_logger,qdrant_store
from app.db import get_celery_session
from app.services import get_chat_service,UpdateChat
from app.utils import text_split
from typing import TypedDict

logger=get_logger(__name__)

class SaveArgs(TypedDict):
    chat_id:str
    title:str
    content:str
    

@celery.task(bind=True,max_retries=3,default_retry_delay=10,name="task_save_original_text_db")
def task_save_original_text_db(self,data:SaveArgs)->SaveArgs:
    try:
        with get_celery_session() as session:
            chat=get_chat_service(session=session)
            details=UpdateChat(title=data.get("title"),original_text=data.get("content"))
            chat.update_chat(chat_id=UUID(data.get("chat_id")),details=details)
        return data
    except Exception as e:
        logger.error(f"Failed to save the text in the db: {str(e)}")
        raise self.retry(exc=e)
    
@celery.task(bind=True,max_retries=3,default_retry_delay=10,name="task_save_original_text_vector_db")
def task_save_original_text_vector_db(self,data:SaveArgs)->SaveArgs:
    try:
        content=text_split(text=data.get("content"))
        qdrant_store.save(texts=content.texts,metadatas=content.metadatas,ids=content.ids)
        return data
    except Exception as e:
        logger.error(f"Failed to store the original text in the vector db: {str(e)}")
        raise self.retry(exc=e)