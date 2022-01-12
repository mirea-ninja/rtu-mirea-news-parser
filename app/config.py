import os
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv(".env")


class Settings:
    api_url: str = os.getenv("API_URL", "https://cms.mirea.ninja/api/")
    api_token: str = os.getenv("API_TOKEN", "")
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
