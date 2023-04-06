from pydantic import BaseSettings


class Settings(BaseSettings):
    ebay_app_id: str
    ms_translate_api_key: str
    ms_translate_api_location: str

    class Config:
        env_file = ".env"
