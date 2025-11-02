from sqlmodel import Field, SQLModel,Column
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from sqlalchemy import String,Enum as SAEnum
from pydantic import EmailStr

class Type(Enum):
    reset="reset-password"
    verification="email-verification"

class Sender(Enum):
    user="user"
    llm="llm"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    first_name: str = Field(default="",nullable=False)
    last_name: str = Field(default="")
    email: EmailStr= Field(default="",sa_type=String(), nullable=False, index=True,unique=True)
    user_name: str = Field(default="", nullable=False, index=True,unique=True)
    password:str=Field(default='',nullable=False)
    created_at:datetime=Field(default_factory=datetime,default=datetime(),nullable=False)
    updated_at:datetime=Field(default_factory=datetime)
    deleted_at:datetime=Field(default_factory=datetime)


class Session(SQLModel,table=True):
    id:UUID=Field(default_factory=uuid4,primary_key=True,index=True)
    user_id:UUID=Field(default_factory=uuid4,nullable=False)
    expires_at:datetime=Field(default_factory=datetime)
    token:str=Field(default_factory=str,default="",nullable=False)
    ip_address:str=Field(default_factory=str,default='',nullable=False)
    user_agent:str=Field(default_factory=str,default='',nullable=False)
    created_at:datetime=Field(default_factory=datetime,default=datetime(),nullable=False)
    updated_at:datetime=Field(default_factory=datetime)

class Token(SQLModel,table=True):
    id:UUID=Field(default_factory=uuid4,index=True,primary_key=True)
    user_id:UUID=Field(default_factory=uuid4,nullable=False)
    type:Type=Field(sa_column=Column(SAEnum(Type)),nullable=False)
    token:str=Field(default_factory=str,default='')
    expires_at:datetime=Field(default_factory=datetime)
    created_at:datetime=Field(default_factory=datetime,default=datetime())

class Docs(SQLModel,table=True):
    id:UUID=Field(default_factory=uuid4,primary_key=True,index=True)
    user_id:UUID=Field(default_factory=uuid4,nullable=False)
    chat_id:UUID=Field(default_factory=uuid4,nullable=False,index=True)
    original_text:str=Field(default='',default_factory=str)
    summary_text:str=Field(default='',default_factory=str)
    audio_url:str=Field(default='',default_factory=str)
    created_at:datetime=Field(default_factory=datetime,default=datetime(),nullable=False)
    updated_at:datetime=Field(default='',default_factory=str)

