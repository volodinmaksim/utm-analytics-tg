from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    ASYNC_DB_URL: str | None = None
    BOT_TOKEN: SecretStr
    REDIS_URL: str | None = None
    BASE_URL: str
    ADMIN_ID: int
    CHAT_ID_TO_CHECK: int
    CHAT_URL: str
    SECRET_TG_KEY: str
    YDISK_LINK: str

    HOST: str
    PORT: int

    @property
    def database_url(self) -> str:
        if self.ASYNC_DB_URL:
            return self.ASYNC_DB_URL
        if self.DB_URL:
            if self.DB_URL.startswith("sqlite:///"):
                return self.DB_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
            return self.DB_URL
        return f"sqlite+aiosqlite:///{BASE_DIR / 'rpp_tg_bot.db'}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
