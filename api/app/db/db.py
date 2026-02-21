from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends
from app.core.logger import get_logger
from app.core.config import config
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, Annotated

logger = get_logger(__name__)
URL = config.database_url


class Database:
    def __init__(
        self,
        url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_recycle: int = 1800,
        echo: bool = False,
    ):
        self.url = url
        self.engine = self._create_engine(pool_size, max_overflow, pool_recycle, echo)

    def _create_engine(
        self, pool_size: int, max_overflow: int, pool_recycle: int, echo: bool
    ):
        try:
            engine = create_engine(
                self.url,
                echo=echo,
                pool_pre_ping=True,
                pool_recycle=pool_recycle,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )
            return engine
        except Exception:
            raise

    def init_db(self) -> None:
        try:
            SQLModel.metadata.create_all(self.engine)
        except SQLAlchemyError:
            raise

    def session(self) -> Generator[Session, None, None]:
        db = Session(self.engine)
        try:
            yield db
        except SQLAlchemyError:
            db.rollback()
            raise

        finally:
            db.close()


db = Database(url=URL)


def get_session() -> Generator[Session, None, None]:
    yield from db.session()


SessionDep = Annotated[Session, Depends(get_session)]
