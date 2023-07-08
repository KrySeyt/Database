from functools import lru_cache

from pydantic import BaseSettings, BaseModel, PostgresDsn, HttpUrl


class DatabaseSettings(BaseModel):
    postgres_dsn: PostgresDsn


class CurrencyExchangeRatesSettings(BaseModel):
    api_url: HttpUrl
    api_key: str | None


class Settings(BaseSettings):
    database: DatabaseSettings
    currency_exchange_rates: CurrencyExchangeRatesSettings

    class Config:
        env_prefix = "BACKEND__"
        env_nested_delimiter = "__"


@lru_cache
def get_settings() -> Settings:
    return Settings()
