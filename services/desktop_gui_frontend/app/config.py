from functools import lru_cache

from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    backend_location: AnyHttpUrl

    class Config:
        env_prefix = "DESKTOP_GUI_FRONTEND__"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
