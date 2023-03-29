from pydantic import BaseSettings


class Settings(BaseSettings):
    ebay_app_id: str
    ms_translate_api_key: str = "0da11c9863204e69a0a743ae54094702"
    ms_translate_api_location: str = "westeurope"

    class Config:
        env_file = ".env"
