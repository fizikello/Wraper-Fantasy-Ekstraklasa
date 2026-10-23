
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str
    db_sslmode: str = "prefer"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
