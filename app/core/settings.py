from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "Lunch Box"
    API_VERSION: str = "/api/v1"
    DATABASE_URL: str
    SLACK_SIGNING_SECRET: str
    SLACK_BOT_TOKEN: str
    LRU_CACHE_SIZE: int = 100
    LRU_CACHE_TTL: int = 60 * 60 * 24  # 1 day


settings = Settings()
