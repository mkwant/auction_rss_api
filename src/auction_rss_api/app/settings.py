from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EBAY_APP_ID: str
    EBAY_APP_SECRET: str
    EBAY_RU_NAME: str
    MS_TRANSLATE_API_KEY: str
    MS_TRANSLATE_API_LOCATION: str
    TRANSLATE_CACHE_DIR: Path = Path('/.translation_cache')
    LOG_LOCATION: Path = Path('/logs/auction_rss_api.log')
    CAMOUFOX_PROFILE_DIR: Path = Path("/app/profile")
    LOG_LEVEL: Literal['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # ty: ignore[missing-argument]


settings = get_settings()
