"""App settings, loaded from environment variables (see .env.example)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./vibe.db"
    music_provider: str = "mock"
    jamendo_client_id: str | None = None
    vibe_model_path: str = "./ml/models/latest"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"


settings = Settings()
