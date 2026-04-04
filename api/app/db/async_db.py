from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator, Annotated
from app.core import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

class AsyncDatabase:
    def __init__(self, url: str):
        self.url = url
        self.engine = create_async_engine(
            self.url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20,
        )
        self._session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except SQLAlchemyError :
                await session.rollback()
                raise
            finally:
                await session.close()
            

db = AsyncDatabase(url=config.database_url)   
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db.session():
        yield session  
                
                
SessionDep = Annotated[AsyncSession, Depends(get_session)]