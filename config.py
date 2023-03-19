from pydantic import BaseSettings


class Settings(BaseSettings):
    ebay_app_id: str

    class Config:
        env_file = ".env"
