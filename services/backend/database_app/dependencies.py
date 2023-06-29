from sqlalchemy.ext.asyncio import AsyncSession

from database_app.database import get_async_engine


async def get_db() -> AsyncSession:
    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        return session


async def get_db_stub() -> None:
    raise NotImplementedError
