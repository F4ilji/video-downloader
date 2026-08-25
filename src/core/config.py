from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "APP_"}

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/video_downloader"
    redis_url: str = "redis://localhost:6379/0"
    downloads_path: str = "/downloads"
    max_concurrent_downloads: int = 4
    yt_dlp_cookies_path: str | None = None
    proxy: str | None = None

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url


settings = Settings()
