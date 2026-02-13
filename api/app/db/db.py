from sqlalchemy.ext.asyncio import create_async_engine
from app.core.logger import get_logger
from app.core.config import config

logger = get_logger()

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

    async def _create_engine(
        self, pool_size: int, max_overflow: int, pool_recycle: int, echo: bool
    ):
        try:
            engine = create_async_engine(
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
