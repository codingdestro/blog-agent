from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_path: str = Field(default="app.db", alias="DATABASE_PATH")
    max_file_chars: int = Field(default=30_000, alias="MAX_FILE_CHARS")
    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    devto_api_key: str | None = Field(default=None, alias="DEVTO_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
