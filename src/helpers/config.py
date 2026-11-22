from dataclasses import Field
from importlib.resources import path
from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER:str
    POSTGRES_PASSWORD:str
    POSTGRES_DB:str
    POSTGRES_PORT:int = 5432
    POSTGRES_HOST:str = "localhost"
    PGADMIN_DEFAULT_EMAIL:str
    PGADMIN_DEFAULT_PASSWORD:str
    PGADMIN_PORT:int = 5050
    CHUNK_SIZE:int = 512000
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALLOW_ADMIN_REGISTRATION: bool = True


    CV_STORAGE_PATH: Path = Path("../data_storage/cv_files")

    model_config = SettingsConfigDict(
        env_file= ".env",
        extra="ignore"
        )

def get_settings():
    return Settings()