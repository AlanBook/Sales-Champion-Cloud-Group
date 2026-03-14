from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "销冠云团 API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./sales_champion.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "sales-champion-demo-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ]
    )
    demo_seed_password: str = "password"
    llm_provider: str = "demo"
    auto_seed_on_startup: bool = False
    embedding_dimensions: int = 16

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
