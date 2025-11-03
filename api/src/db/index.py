from lib.logger import get_logger
from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends

load_dotenv()
logger=get_logger("db/index")

DATABASE_URI=os.getenv("DATABASE_URI")
# logger.info(f"Database url: {DATABASE_URI}")


connect_args={}
conn=create_engine(DATABASE_URI,connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(conn)

def get_session():
    with Session(conn) as session:
        yield session

SessionDep=Annotated[Session,Depends(get_session)]