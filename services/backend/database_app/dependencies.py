from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from database_app.database import get_async_engine


async def get_db() -> AsyncIterator[AsyncSession]:
    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        yield session


async def get_db_stub() -> None:
    raise NotImplementedError
