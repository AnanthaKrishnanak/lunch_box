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


settings = Settings()
