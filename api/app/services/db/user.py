from app.models.all_schema import User
from sqlmodel import Session as SessionDep
from app.schemas.db import user
from app.utils.logger import get_logger
from app.services.auth.password import get_hashed_password, verify_password
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import EmailStr
from sqlmodel import select
from typing import Optional
from app.schemas import response
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
                status_code=status.HTTP_401_UNAUTHORIZED,
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
    if not email:
        raise TypeError("No email found")

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


def create_user(user: user.UserCreate, session: SessionDep) -> response.Response:
    """Creating the user with the email and password"""
    try:
        logger.info("Registering the user")
        old_user = get_user_by_email(email=user["email"], session=session)
        if old_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email alreay exists, please try another email",
            )
        new_user: User = User(email=user["email"], password=user["password"])
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"Successfully registered the user with the id:{new_user.id}")
        return response.Response(
            status="success",
            message="Successfully registered",
            data={"id": new_user.id, "email": new_user.email},
        )
    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to register the user with the email:{user['email']},error: {str(e)}",
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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No user found with gith given id",
            )

        updated_data = details.model_dump(exclude_unset=True)

        for field, value in updated_data.items():
            setattr(old_user, field, value)

        session.add(old_user)
        session.commit()
        session.refresh(old_user)

        logger.debug(
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
                status_code=status.HTTP_401_UNAUTHORIZED,
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


# update password
def update_user_password(
    data: user.UpdatePassword, session: SessionDep
) -> response.Response:
    """Updating the user password"""
    try:
        logger.debug("Update user password")
        old_user = get_user_by_id(user_id=data.user_id, session=session)
        if not old_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user found",
            )

        check_password = verify_password(
            plain_password=data.old_password, hashed_password=old_user.password
        )
        if not check_password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Password does not match please check the password",
            )

        new_hashed_password = get_hashed_password(data.new_password)
        new_user: User = User(password=new_hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return response.Response(
            status="success",
            message="Successfully updated the password",
        )
    except HTTPException:
        raise

    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(
            f"Failed to update the user password:{user['email']},error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )

    except Exception as e:
        session.rollback()
        logger.error(
            f"Unexpected error while updating the user password: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
