from functools import partial
import asyncio
from typing import Callable


async def run_sync[T](func: Callable[..., T], *args, **kwargs) -> T:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))
