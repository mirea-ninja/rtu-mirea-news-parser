from functools import lru_cache

from pydantic import AnyHttpUrl, BaseSettings, Field


class Config(BaseSettings):
    API_URL: AnyHttpUrl = Field(..., env="API_URL")
    API_TOKEN: str = Field(..., env="API_TOKEN")
    USE_EMBEDDED_SCEDULER: bool = Field(..., env="USE_EMBEDDED_SCEDULER")

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings() -> Config:
    return Config()
