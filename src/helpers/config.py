from pathlib import Path

from pydantic_settings import BaseSettings,SettingsConfigDict

# src/ directory, so the .env file is found no matter which
# directory the process (uvicorn, alembic, ...) is started from.
SRC_DIR = Path(__file__).resolve().parent.parent


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
    GROQ_API_KEY:str = None
    GROQ_API_URL:str = None
    INPUT_MAX_CHARACTER:int = None
    MAX_OUTPUT_TOKENS:int = None
    TEMPERATURE:float = None
    GENERATION_BACKEND:str = None
    GENERATION_MODEL_ID:str = None
    HUGGINGFACE_MODEL_NAME:str = None





    model_config = SettingsConfigDict(
        env_file=SRC_DIR / ".env",
        extra="ignore"
        )

def get_settings():
    return Settings()