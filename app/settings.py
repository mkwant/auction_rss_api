from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ebay_app_id: str
    ebay_app_secret: str
    ebay_ru_name: str
    ms_translate_api_key: str
    ms_translate_api_location: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
