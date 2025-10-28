from lib.celery import celery
from lib.logger import get_logger

logger = get_logger("workers/query")


@celery.task(bind=True, max_retries=3)
def handle_query(self, chat_id:str, user_id:str, question_id:str,question:str):
    try:
        if not chat_id or not user_id or not question or not question_id:
            logger.error("Missing parameters in handle_query task")
            return {
                "status":"error",
                "message":"missing paramerters",
                "code":400,
                "data":None
            }
        
        if chat_id.strip()=="" or question.strip()=="" or question_id.strip()=="" or user_id.strip()=="":
            logger.error("Empty parameters in the handle_query task")
            return {
                "status":"error",
                "message":"Empty parameter is not allowed",
                "code":400,
                "data":None
            }
        
        if not isinstance(question,str):
            logger.error("Question must be string")
            return {
                "status":"error",
                "message":"Question is not string",
                "code":400,
                "data":None
            }
        
        question=question.strip()

        if len(question)>10:
            logger.error("Question length too sort")
            return {
                "status":"error",
                "message":"question is too sort"
            }
        
        # ====Getting the docs from the vector store=====
        try:
            logger.info("Started processing the task for getting similer docs from the vectorstore ")
            from workers.vectors.get_data import search_chunks_in_vectorstore
            response=search_chunks_in_vectorstore.delay(query=question,chat_id=chat_id,user_id=user_id)
            logger.info("Successfully got the chunks for the question")
        
        except Exception as e:
            logger.error("Failed to queue")