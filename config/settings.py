from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_base_url: str = Field(alias="API_BASE_URL")
    api_v1_base_url: str = Field(default="https://api.stage2.surfsight.net/user_api/api", alias="API_V1_BASE_URL")
    api_timeout: float = Field(default=10.0, alias="API_TIMEOUT")
    openapi_path: str = Field(default="openapi/openapi.json", alias="OPENAPI_PATH")
    run_fuzz: bool = Field(default=False, alias="RUN_FUZZ")
    run_integration: bool = Field(default=False, alias="RUN_INTEGRATION")
    env: str = Field(default="local", alias="ENV")

    auth_username: str = Field(default="qa_user", alias="AUTH_USERNAME")
    auth_password: str = Field(default="qa_password", alias="AUTH_PASSWORD")

    api_retries: int = Field(default=2, alias="API_RETRIES")
    api_retry_backoff: float = Field(default=0.2, alias="API_RETRY_BACKOFF")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def openapi_full_path(self) -> Path:
        return Path(self.openapi_path).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
