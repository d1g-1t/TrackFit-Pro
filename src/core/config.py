from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "TrackFit Pro API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


def _validate_secret_key(settings: Settings) -> Settings:
    if len(settings.SECRET_KEY) < 32 and not settings.SECRET_KEY.startswith("dummy-"):
        import warnings

        warnings.warn(
            "SECRET_KEY is less than 32 characters. Use a strong key in production.",
            UserWarning,
            stacklevel=2,
        )
    return settings


@lru_cache
def get_settings() -> Settings:
    settings = Settings()  # type: ignore[call-arg]
    return _validate_secret_key(settings)


settings = get_settings()
