from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):

    JWT_SK: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    CONNECTION_STRING: str
        
    class Config:
        env_file:str = ".env"
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings():
    return Settings()