from app.utils import HandlePassword
from sqlmodel import select
from typing import Optional
from uuid import UUID
from app.db import AsyncDatabaseService
from app.db.schemas import Users
from app.core import get_logger
from sqlalchemy.exc import SQLAlchemyError
from app.models import CreateUser,UpdateChat,Response
from app.core import DBErrorException,NotFoundException,AppException
from app.utils import run_sync

logger=get_logger(__name__)


class FindUser:
    def __init__(self,db:AsyncDatabaseService):
        self._db = db
    
    async def get_user_by_id(self,user_id:UUID)->Optional[Users]:
        try:
            logger.debug(f"Fetching user by id={user_id}")
            return await self._db.session.get(Users, user_id)
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch user by id={user_id}",
            )
            raise DBErrorException("Failed to fetch the user by id") from e
    
    async def get_user_by_email(self,email:str)->Optional[Users]:
        try:
            logger.debug(f"Fetching user by email={email}")
            statement = select(Users).where(Users.email == email)
            result = await self._db.session.execute(statement)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to fetch user by email={email}",
            )
            raise DBErrorException("Failed to fetch the user by email") from e
        
class UserService:
    def __init__(self,db:AsyncDatabaseService,password:HandlePassword,find_user:FindUser) -> None:
        self._db = db
        self._password = password
        self._user = find_user
        
    async def get_current_user(self,user_id:UUID):
        try:
            old_user=await self._user.get_user_by_id(user_id)
            
            if not old_user:
                raise NotFoundException("User not found")
            return old_user
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch user by id={user_id}",
            )
            raise Exception("Failed to fetch the user by id") from e
        
    async def create_user(self,data:CreateUser)->Response:
        try:
            existing=await self._user.get_user_by_email(data.email)
            if existing:
                raise AppException(message="Email already exists",status_code=409)
            
            hashed_password=await run_sync(self._password.get_hashed_password,data.password)
            
            new_user=Users(email=data.email,password=hashed_password)
            self._db.add(new_user)
            await self._db.session.commit()
            await self._db.session.refresh(new_user)
            
            logger.info(f"User created with id={new_user.id}")
            
            return Response(data={"id": str(new_user.id), "email": new_user.email})
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "User creation failed",
            )
            raise Exception("Failed to create user") from e
    
    async def update_user(self,user_id:UUID,data:UpdateChat)->Response[Users]:
        try:
            if not data.has_update():
                raise AppException(message="No fields to update",status_code=400)
            old_user=await self._user.get_user_by_id(user_id)
            if not old_user:
                raise NotFoundException("User not found")
            updates=data.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(old_user, field, value)
            self._db.add(old_user)
            await self._db.session.commit()
            await self._db.session.refresh(old_user)
            logger.info(f"User updated id={user_id}, fields={list(updates.keys())}")
            return Response(data=old_user)
        except (NotFoundException, AppException):
            raise
        except Exception as e:
            logger.error(
                f"Failed to update user id={user_id}",
            )
            raise Exception("Failed to update user") from e
        
    async def delete_user(self,user_id:UUID)->Response[str]:
        try:
            old_user=await self._user.get_user_by_id(user_id)
            if not old_user:
                raise NotFoundException("User not found")
            await self._db.session.delete(old_user)
            await self._db.session.commit()
            logger.info(f"User deleted with id={user_id}")
            return Response(data="User deleted successfully")
        
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to delete user id={user_id}",
            )
            raise Exception("Failed to delete user") from e