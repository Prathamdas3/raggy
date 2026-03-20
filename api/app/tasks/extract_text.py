from app.core import celery,get_logger
from app.models import ExtractChat
from app.utils import extract_pdf_content_from_path
from typing import TypedDict
from app.tasks.save_text import SaveArgs

logger=get_logger(__name__)

class ExtractedDictType(TypedDict):
    doc_id:str
    file_path:str
    file_type:str

@celery.task(bind=True,max_retries=3,default_retry_delay=10,name="task_extract_text")
def task_extract_text(self,data:ExtractedDictType)->SaveArgs:
    try:
        data=ExtractChat(**data).model_dump()
        content=extract_pdf_content_from_path(path=data.file_path)
        if not content.title or not content.content:
            raise ValueError("No content found from the given file path")
        return {
            "title":content.title,
            "content":content.content,
            "chat_id":str(data.doc_id)
        }
    except Exception as e:
        logger.error(f"Failed to extract the file content of type {data.get("file_type")}:{str(e)}")
        raise self.retry(exc=e)
    
    