from app.models.all_schema import User
from app.configs.database import SessionDep
from app.utils.logger import get_logger
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import EmailStr
from sqlmodel import select
from typing import Optional
from app.schemas import response, auth, user
from uuid import UUID

logger = get_logger(__name__)


def get_user_by_id(user_id: UUID, session: SessionDep) -> User:
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

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to get the user with the id:{user_id},error: {str(e)}",
            exc_info=True,
        )
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

    except (IntegrityError, SQLAlchemyError) as e:
        logger.error(
            f"Failed to get the user with the email:{email},error: {str(e)}",
            exc_info=True,
        )
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


def create_user(user: auth.UserCreate, session: SessionDep) -> response.Response:
    """Creating the user with the email and password"""
    try:
        logger.info("Registering the user")
        old_user = get_user_by_email(email=user.email)
        if old_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email alreay exists, please try another email",
            )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Successfully registered the user with the id:{user.id}")
        return response.Response(
            status="success",
            message="Successfully registered",
            data={"id": user.id, "email": user.email},
        )
    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to register the user with the email:{user.email},error: {str(e)}",
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


def update_user_details(
    details: user.UpdateUser, user_id: UUID, session: SessionDep
) -> response.Response:
    """Updating the user with details"""
    try:
        if not details.has_updates():
            logger.info(
                f"Update attempt with no fields for user details for the user_id:{user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        logger.info(f"Updating the user details for the user id:{user_id}")
        old_user = get_user_by_id(user_id=user_id, session=session)

        if not old_user:
            logger.error(f"No user found with the given user id:{user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found with gith given id",
            )

        updated_data = details.model_dump(exclude_unset=True)

        for field, value in updated_data.items():
            setattr(old_user, field, value)

        session.add(old_user)
        session.commit()
        session.refresh(old_user)

        logger.info(
            f"Successfully updated the user details for the user with the id:{user_id}, with the fields: {list(updated_data.keys())}"
        )

        return response.Response(
            status="success", message="Successfully updated the user with the details"
        )
    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to update the user with the id:{user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while removing user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def delete_user_by_id(user_id: UUID, session: SessionDep) -> response.Response:
    """Deleting a user based on the id"""
    try:
        logger.info(f"Starting to delete the user with the id: {user_id}")
        old_user = get_user_by_id(user_id=user_id, session=session)
        if not old_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found with this user_id",
            )

        session.delete(old_user)
        session.commit()
        logger.info("Successfully removed the user from the db")
        return response.Response(
            status="success",
            message="Successfully removed the user",
            data={
                "id": user_id,
                "email": old_user.email,
                "name": f"{old_user.first_name} {old_user.last_name}",
            },
        )

    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to remove the user with the id:{user_id},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error while removing user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
