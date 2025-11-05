from pydantic import BaseModel,field_validator,EmailStr
from typing import Optional
import re

class UserCreate(BaseModel):
    email:EmailStr
    password:str

    @field_validator("email","password",mode="before")
    def verify_fields(cls,v,field):
        if not isinstance(v,str):
            raise TypeError(f"{field.name} must be a string")
        
        if not v.strip():
            raise ValueError(f"{field.name} cannot be empty or whitespace")
        
        return v.strip()
    
    @field_validator("password",mode="before")
    def validate_password(cls,v):
        if not isinstance(v, str):
            raise TypeError("Password must be a string")

        v = v.strip()
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v

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
