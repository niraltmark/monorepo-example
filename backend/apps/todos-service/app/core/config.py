from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Todos Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/todos_db"

    USERS_SERVICE_URL: str = "http://localhost:8001"

    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    REDIS_URL: str = "redis://localhost:6379"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
