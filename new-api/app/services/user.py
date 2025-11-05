from app.models.all_schema import User
from app.configs.database import SessionDep
from app.utils.logger import get_logger
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import EmailStr
from sqlmodel import select
from typing import Optional
from app.schemas import response,auth,user

logger = get_logger(__name__)


def get_user_by_id(user_id: str, session: SessionDep) -> User:
    """Getting the user from the user id"""
    if not user_id or not isinstance(user_id, str):
        raise ValueError("No user id found ")

    if user_id.strip():
        raise ValueError("User id can not be empty")

    try:
        logger.info(f"Fetching the user with the id of {user_id}")
        user_id = user_id.strip()

        user = session.get(User, user_id)

        if not user:
            logger.info(f"No user found {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found with the given id",
            )

        logger.info(f"Successfully fetched the user with the user_id:{user_id}")
        return user

    except HTTPException:
        raise

    except IntegrityError as e:
        logger.error(
            f"Failed to get the user with the id:{user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch user with id: {user_id},error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while getting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def get_user_by_email(email: EmailStr, session: SessionDep) -> Optional[User]:
    """Fetching the user based on email"""
    if not email or not isinstance(email, EmailStr):
        raise ValueError("No email found")

    if not email.strip():
        raise ValueError("Email can have a empty value")

    try:
        logger.info(f"Starting to fetch the uesr with the email:{email}")
        statement = select(User).where(User.email == email)
        user = session.exec(statement=statement).first()

        if not user:
            logger.info(f"No user found {email}")
            return None

        logger.info("Successfully fetched the user with email:{email}")
        return user
    
    except IntegrityError as e:
        logger.error(
            f"Failed to get the user with the email:{email},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch user with email: {email},error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        logger.error(f"Unexpected error while getting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def create_user(user:auth.UserCreate,session:SessionDep)->User:
    """Creating the user with the email and password"""
    pass

def update_user_details(details:user.UpdateUser,session:SessionDep)->User:
    """Updating the user with details"""
    pass

def delete_user_by_id(user_id:str,session:SessionDep)->response.Response:
    """Deleting a user based on the id"""
    pass
