import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.services.jwt_keys import private_key_gl, public_key_gl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields
    )
    settings_is_debug: bool = Field(default=False, alias="settings_is_debug")
    project_name: str = Field(default="FastAPI Authorization", alias="PROJECT_NAME")

    pg_name: str = Field(default="db", alias="POSTGRES_DB")
    pg_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    pg_port: int = Field(default=5432, alias="POSTGRES_PORT")
    pg_user: str = Field(default="user", alias="POSTGRES_USER")
    pg_password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    pg_echo: bool = Field(default=True, alias="POSTGRES_ECHO")

    cache_expire_sec: int = Field(default=300, alias="CACHE_EXPIRE_SEC")
    page_size: int = Field(default=100, alias="PAGE_SIZE")

    private_key: str = Field(default=private_key_gl, alias="PRIVATE_KEY_GL")
    public_key: str = Field(default=public_key_gl, alias="PUBLIC_KEY_GL")

    algorithm: str = Field(default="RS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @property
    def async_db_url(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_name}"


settings = Settings()
