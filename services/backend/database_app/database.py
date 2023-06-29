from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class DBModelBase(DeclarativeBase):
    pass


def get_postgres_url() -> str:
    postgres_url = get_settings().database.postgres_dsn
    postgres_url_with_connector = f"postgresql+asyncpg{postgres_url[postgres_url.find(':'):]}"
    return postgres_url_with_connector


@lru_cache()
def get_async_engine() -> AsyncEngine:
    return create_async_engine(get_postgres_url())
