from app.core import celery,get_logger
from typing import TypedDict

logger=get_logger(__name__)

class SaveArgs(TypedDict):
    doc_id:str
    title:str
    content:str
    

@celery.task(bind=True,max_retries=3,default_retry_delay=10,name="task_save_text")
def task_save_task(self,):
    ...