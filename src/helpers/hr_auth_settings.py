from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# src/ directory -> reads the same src/.env file as helpers/config.py
SRC_DIR = Path(__file__).resolve().parent.parent


class HRAuthSettings(BaseSettings):
    """Auth settings for the HR portal.

    Kept separate from helpers/config.py so that file does not need editing.
    """

    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Set to false once your company/admin accounts exist, to close public sign-up.
    ALLOW_ADMIN_REGISTRATION: bool = True

    model_config = SettingsConfigDict(env_file=SRC_DIR / ".env", extra="ignore")


@lru_cache
def get_hr_auth_settings() -> HRAuthSettings:
    return HRAuthSettings()
