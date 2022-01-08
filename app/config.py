import os
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv(".env")


class Settings:
    api_url: str = os.getenv("API_URL", "http://localhost:1337/api/")
    api_token: str = os.getenv("API_TOKEN", "dda2b01e33cb0778280fc728b5d4c2a3")


@lru_cache
def get_settings() -> Settings:
    return Settings()
