from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EBAY_APP_ID: str
    EBAY_APP_SECRET: str
    EBAY_RU_NAME: str
    MS_TRANSLATE_API_KEY: str
    MS_TRANSLATE_API_LOCATION: str
    LOG_LEVEL: Literal['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
