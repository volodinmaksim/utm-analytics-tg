from functools import lru_cache

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/users.db"
    BOT_TOKEN: SecretStr
    BASE_URL: str
    ADMIN_ID: int
    CHAT_ID_TO_CHECK: int
    CHAT_URL: str
    SECRET_TG_KEY: str
    YDISK_LINK: str

    HOST: str
    PORT: int

    @computed_field
    @property
    def WEBHOOK_PATH(self) -> str:
        return f"/{self.BOT_TOKEN.get_secret_value()}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
