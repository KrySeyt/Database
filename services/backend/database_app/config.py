from functools import lru_cache

from pydantic import BaseSettings, BaseModel, PostgresDsn


class DatabaseSettings(BaseModel):
    postgres_dsn: PostgresDsn


class Settings(BaseSettings):
    database: DatabaseSettings

    class Config:
        env_prefix = "BACKEND__"
        env_nested_delimiter = "__"


@lru_cache
def get_settings() -> Settings:
    return Settings()
