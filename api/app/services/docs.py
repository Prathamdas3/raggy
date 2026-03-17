from fastapi import HTTPException,status
from uuid import UUID

from app.db import Docs, DatabaseService
from app.core import get_logger

logger=get_logger(__name__)

class DocsService:
    def __init__(self, db_session: DatabaseService):
        self._db: DatabaseService = db_session

    def find_docs(self,doc_id)->Docs:
        try:
            docs=self._db.session.get(Docs,doc_id)
            if not docs:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No docs found with the given id")
            return docs
        except HTTPException:
            raise
        except Exception:
            logger.error(f"No docs found with the given id: {doc_id}",exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong while fetching the the docs"
            )
    def create_docs(self, user_id: UUID) -> UUID:
        try:
            docs = Docs(user_id=user_id)
            self._db.session.add(docs)
            self._db.commit()
            self._db.session.refresh(docs)
            return docs.id
        except Exception as e:
            logger.error("Failed to create a new docs", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store the docs",
            ) from e

    def remove_docs(self,doc_id:UUID)->str:
        try:
            doc=self.find_docs(doc_id=doc_id)
            self._db.session.delete(doc)
            self._db.commit()
            logger.info(f"Successfully removed the docs with the id: {doc_id}")
            return "Successfully removed the docs"
        except Exception:
            logger.error("Failed to remove the docs", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove the docs",
            ) 
            
    def update_docs(self,doc_id:UUID,original_text:str):
        try:
            doc=self.find_docs(doc_id=doc_id)
            setattr(doc,original_text,original_text)
            self._db.session.add(doc)
            self._db.commit()
            self._db.session.refresh(doc)
            return "Successfully updated the docs"
        except Exception:
            logger.error("Failed to update the docs with the original text")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add original text"
            )