from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    user_id:str
    email:str
    full_name:str


class Token(BaseModel):
    access_token:str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    token_type: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
