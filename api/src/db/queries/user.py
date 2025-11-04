from lib.logger import get_logger
from db.index import SessionDep
from db.schema import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

logger = get_logger("db/queries/user")


def create_user(user: User, session: SessionDep):
    try:
        logger.info("Staring the process of creating the user")
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Successfully created the user:{user.id}")
        return user
    except IntegrityError as e:
        session.rollback()
        logger.error(
            f"Violation of database consistancy while creating the user: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Violation of database consistancy while creating the user",
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(
            f"Failed to create the user due to some database error:{str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the user, internal server error",
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create the user {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    

