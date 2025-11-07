from app.models.all_schema import Session
from sqlmodel import Session as SessionDep
from app.utils.logger import get_logger
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.auth import SessionCreate, GetSessionReq
from app.schemas.response import Response
from typing import Optional
from sqlmodel import select

logger = get_logger(__name__)


def create_session(data: SessionCreate, session: SessionDep) -> Response:
    try:
        logger.info("Creating session")
        new_session: Session = Session(
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            user_id=data.user_id,
            expires_at=data.expires_at,
            token=data.token,
        )
        session.add(new_session)
        session.commit()
        session.refresh(new_session)
        logger.info("Successfully created the session")
        return Response(status="success", message="successfully created the session")
    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to create the session for the user id: {data.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while registering user: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_session(data: GetSessionReq, session: SessionDep) -> Optional[Session]:
    try:
        logger.debug("Starting find the session with the user id")
        statement = (
            select(Session)
            .where(Session.user_id == data.user_id)
            .where(Session.token == data.token)
        )
        old_session = session.exec(statement=statement).first()

        if not old_session:
            logger.info("No user session exists")
            return None

        logger.debug("Successfully found the ")
        return Session

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to get the session for the user id: {data.user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(
            f"Failed to find the session with the user_id:,error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find the session",
        )


def remove_session(old_session: Session, session: SessionDep) -> Response:
    if not old_session or not isinstance(old_session, Session):
        raise TypeError("No session found")

    try:
        logger.debug("Starting to remove the session")
        session.delete(old_session)
        session.commit()
        logger.debug("Successfully removed the session")
        return Response(status="success", message="removed the session successfully")
    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to remove the session,error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
    except Exception as e:
        logger.error(f"Failed to remove the session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log out",
        )
