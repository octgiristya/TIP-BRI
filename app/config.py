import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongo_host: str = "172.18.170.203"
    mongo_port: int = 27017
    mongo_database: str = "cia_dashboard"
    secret_key: str = "supersecretkey_change_in_production"
    session_key: str = "session_secret_change_in_production"
    upload_path: str = "./upload"
    totp_secret: str = "4L7NVTH6QT37TWRTGHDFH62H5FNUR66C"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
