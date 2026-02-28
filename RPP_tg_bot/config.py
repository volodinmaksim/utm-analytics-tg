from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DB_URL: str
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

    @staticmethod
    def _replace_db_driver(url: str, driver: str) -> str:
        parsed = urlsplit(url)
        scheme = parsed.scheme.split("+", 1)[0]
        return urlunsplit(
            (
                f"{scheme}+{driver}",
                parsed.netloc,
                parsed.path,
                parsed.query,
                parsed.fragment,
            )
        )

    @computed_field
    @property
    def ASYNC_DB_URL(self) -> str:
        if "+" in self.DB_URL.split(":", 1)[0]:
            return self.DB_URL
        return self._replace_db_driver(self.DB_URL, "asyncpg")

    @computed_field
    @property
    def SYNC_DB_URL(self) -> str:
        if "+" not in self.DB_URL.split(":", 1)[0]:
            return self.DB_URL

        if find_spec("psycopg") is not None:
            sync_driver = "psycopg"
        elif find_spec("psycopg2") is not None:
            sync_driver = "psycopg2"
        else:
            sync_driver = "psycopg2"

        return self._replace_db_driver(self.DB_URL, sync_driver)

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
