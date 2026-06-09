# config.py file, database and security object

from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str= "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "auth"

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    JWT_SECRET_KEY :str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()