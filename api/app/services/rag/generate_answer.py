from app.schemas.rag.query import QueryInput
from app.services.common.model import get_response
from app.configs.qdrant import get_vector_store
# from qdrant_client import models
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_answer(data: QueryInput) -> str:
    try:
        vector_store = get_vector_store()
    except Exception as e:
        logger.error(f"Failed to get the vector store: {str(e)}", exc_info=True)
        raise ValueError("Failed to get the vector store")

    try:
        logger.debug("Creating the retriver....")
        retriever = vector_store.similarity_search(
            query=data.question,
            k=1,
            # filter=models.Filter(
            #     must=[
            #         models.FieldCondition(
            #             key="metadata.chat_id",
            #             match=models.MatchValue(value=str(data.chat_id)),
            #         ),
            #         models.FieldCondition(
            #             key="metadata.user_id",
            #             match=models.MatchValue(value=str(data.user_id)),
            #         ),
            #     ]
            # ),
        )

        content = "\n".join([doc.page_content for doc in retriever])

        if not isinstance(content, str) or not content.strip():
            logger.error("content is empty from retriver")
            raise ValueError("No matched content found in the document ")

        content = content.strip()

    except Exception:
        logger.error("Failed to get the content for the context", exc_info=True)
        raise ValueError("Failed to get the content using the context")

    try:
        logger.debug("Generating answer using language model")

        answer,_ = get_response(query=content, question=data.question)

        if not answer or not answer.strip():
            logger.error("Failed generate the answer")
            raise ValueError("No answer generated")

        if not isinstance(answer, str):
            logger.warning(f"Answer is not string: {type(answer)}, converting")
            answer = str(answer)

        answer = answer.strip()

    except Exception as e:
        logger.error(f"Failed to generate answers error: {str(e)}",exc_info=True)
        raise ValueError("NO answer got generated")

    return answer
