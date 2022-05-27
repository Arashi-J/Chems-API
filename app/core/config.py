from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    CONNECTION_STRING: str
        
    class Config:
        env_file:str = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()