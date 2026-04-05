from pydantic import EmailStr
from app.core import get_logger
from app.models import CreateUser, SigninUser, UpdatePassword
from app.db import AsyncDatabaseService
from app.utils import run_sync,HandlePassword
from app.services.user import FindUser
from app.core import AppException
from dataclasses import dataclass

@dataclass
class CreateNewUser:
    email: EmailStr
    id: str


logger = get_logger(__name__)


class AuthService:
    def __init__(self,db:AsyncDatabaseService,password:HandlePassword,user:FindUser):
        self._db = db
        self._password = password
        self._user = user
    async def user_signup(self,data:CreateUser) -> CreateNewUser:
        try:
            existing=await self._user.get_user_by_email(data.email)
            if existing:
                raise AppException("Email already exists",status_code=409)
            hashed_password=await run_sync(self._password.get_hashed_password,data.password)
            from app.db.schemas import Users
            new_user=Users(email=data.email,password=hashed_password)
            self._db.add(new_user)
            await self._db.commit()
            await self._db.refresh(new_user)
            return CreateNewUser(id=str(new_user.id), email=new_user.email)
        except AppException:
            raise
        except Exception as e: 
            logger.error(f"Error during user signup: {e}")
            raise AppException("Failed to sign up user",status_code=500)
        
    async def user_signin(self,data:SigninUser)->CreateNewUser:
        try:
            user=await self._user.get_user_by_email(data.email)
            if not user:
                raise AppException("Invalid email or password",status_code=401)
            password_valid=await run_sync(self._password.verify_password,data.password,user.password)
            if not password_valid:
                raise AppException("Invalid email or password",status_code=401)
            return CreateNewUser(id=str(user.id), email=user.email)
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Error during user signin: {e}")
            raise AppException("Failed to sign in user",status_code=500)
        
    async def update_password(self,data:UpdatePassword)->str:
        try:
            user=await self._user.get_user_by_id(data.user_id)
            if not user:
                raise AppException("User not found",status_code=404)
            password_valid=await run_sync(self._password.verify_password,data.old_password,user.password)
            if not password_valid:
                raise AppException("Invalid old password",status_code=401)
            new_hashed_password=await run_sync(self._password.get_hashed_password,data.new_password)
            user.password=new_hashed_password
            self._db.add(user)
            await self._db.commit()
            return "Password updated successfully"
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Error during password update: {e}")
            raise AppException("Failed to update password",status_code=500)